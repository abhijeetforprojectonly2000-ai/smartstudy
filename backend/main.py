# main.py - Complete FastAPI Backend 
from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import pdfplumber
import io
import os
import json
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import shutil
from pathlib import Path
from urllib.parse import quote_plus
import PyPDF2
import fitz  

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# ============================================================================
# CONFIGURATION
# ============================================================================
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "beyondchats_db")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "meta-llama/llama-3.2-3b-instruct:free"  # Using free model
UPLOAD_DIR = "./uploads"

# Create upload directory
Path(UPLOAD_DIR).mkdir(exist_ok=True)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
class Database:
    client: Any = None
    
db = Database()

async def connect_db():
    """Connect to MongoDB with secure logging"""
    try:
        mongodb_uri = MONGODB_URI
        
        db.client = AsyncIOMotorClient(mongodb_uri)
        
        # Test the connection
        await db.client.admin.command('ping')
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ MongoDB Connection Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Check Network Access whitelist in MongoDB Atlas")
        print("   2. Verify database user credentials")
        print("   3. Ensure connection string format is correct")
        raise

async def close_db():
    if db.client:
        db.client.close()
        print("❌ Closed MongoDB connection")

def get_database():
    if db.client is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    return db.client[DATABASE_NAME]

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================
class QuizQuestion(BaseModel):
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    question_type: str

class QuizGenerateRequest(BaseModel):
    pdf_id: Optional[str] = None
    num_mcq: int = 5
    num_saq: int = 3
    num_laq: int = 2

class QuizAnswer(BaseModel):
    question_index: int
    user_answer: str

class QuizSubmitRequest(BaseModel):
    quiz_id: str
    answers: List[QuizAnswer]

class ChatRequest(BaseModel):
    chat_id: Optional[str] = None
    message: str
    pdf_id: Optional[str] = None

class YouTubeRequest(BaseModel):
    topic: str
    pdf_id: Optional[str] = None

# ============================================================================
# UTILITY FUNCTIONS 
# ============================================================================
def extract_text_with_pdfplumber(pdf_path: str) -> Dict[str, str]:
    """Method 1: Extract using pdfplumber"""
    pages_text = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text[str(i + 1)] = text
        return pages_text
    except Exception as e:
        print(f"⚠️  pdfplumber failed: {str(e)}")
        return {}

def extract_text_with_pypdf2(pdf_path: str) -> Dict[str, str]:
    """Method 2: Extract using PyPDF2"""
    pages_text = {}
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(pdf_reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text[str(i + 1)] = text
        return pages_text
    except Exception as e:
        print(f"⚠️  PyPDF2 failed: {str(e)}")
        return {}

def extract_text_with_pymupdf(pdf_path: str) -> Dict[str, str]:
    """Method 3: Extract using PyMuPDF (fitz)"""
    pages_text = {}
    try:
        doc = fitz.open(pdf_path)
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text() or ""
            if text.strip():
                pages_text[str(i + 1)] = text
        doc.close()
        return pages_text
    except Exception as e:
        print(f"⚠️  PyMuPDF failed: {str(e)}")
        return {}

def extract_text_from_pdf(pdf_path: str) -> Dict[str, str]:
    """Extract text from PDF using multiple methods as fallback"""
    print(f"📄 Attempting to extract text from: {pdf_path}")
    
    pages_text = extract_text_with_pdfplumber(pdf_path)
    if pages_text:
        print(f"✅ Extracted {len(pages_text)} pages using pdfplumber")
        return pages_text
    
    print("📄 Trying PyMuPDF...")
    pages_text = extract_text_with_pymupdf(pdf_path)
    if pages_text:
        print(f"✅ Extracted {len(pages_text)} pages using PyMuPDF")
        return pages_text
    
    print("📄 Trying PyPDF2...")
    pages_text = extract_text_with_pypdf2(pdf_path)
    if pages_text:
        print(f"✅ Extracted {len(pages_text)} pages using PyPDF2")
        return pages_text
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        
        if total_pages > 0:
            print(f"⚠️  PDF has {total_pages} pages but no extractable text")
            return {str(i + 1): "[Image-based page - OCR needed]" for i in range(total_pages)}
    except:
        pass
    
    raise HTTPException(
        status_code=422, 
        detail="Unable to extract text from PDF. The file might be corrupted, password-protected, or image-based."
    )

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_size += len(word) + 1
        if current_size > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = len(word)
        else:
            current_chunk.append(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

async def call_llm(prompt: str, system_prompt: str = "You are a helpful AI assistant.", use_fallback: bool = True) -> str:
    """Call OpenRouter API with improved error handling and fallback"""
    
    # Check if API key is configured
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_key_here":
        print("⚠️  OpenRouter API key not configured. Using fallback response.")
        if use_fallback:
            return get_fallback_response(prompt, system_prompt)
        else:
            raise HTTPException(
                status_code=503,
                detail="AI service not configured. Please set OPENROUTER_API_KEY in environment variables."
            )
    
    try:
        print(f"🤖 Calling LLM API with model: {MODEL_NAME}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "BeyondChats Teacher Assistant",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL_NAME,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            # Log response status
            print(f"📡 API Response Status: {response.status_code}")
            
            if response.status_code == 401:
                print("❌ Invalid API Key")
                if use_fallback:
                    return get_fallback_response(prompt, system_prompt)
                raise HTTPException(status_code=503, detail="Invalid API key")
            
            if response.status_code == 429:
                print("⚠️  Rate limit exceeded")
                if use_fallback:
                    return get_fallback_response(prompt, system_prompt)
                raise HTTPException(status_code=503, detail="API rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()
            
            # Extract content from response
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                print(f"✅ LLM Response received ({len(content)} chars)")
                return content
            else:
                print("❌ Unexpected API response format")
                if use_fallback:
                    return get_fallback_response(prompt, system_prompt)
                raise HTTPException(status_code=503, detail="Unexpected API response format")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ LLM API HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text[:200]}")
        if use_fallback:
            return get_fallback_response(prompt, system_prompt)
        raise HTTPException(
            status_code=503,
            detail=f"AI service error: {e.response.status_code}"
        )
    except httpx.TimeoutException:
        print("❌ LLM API Timeout")
        if use_fallback:
            return get_fallback_response(prompt, system_prompt)
        raise HTTPException(
            status_code=503,
            detail="AI service timeout. Please try again."
        )
    except Exception as e:
        print(f"❌ LLM API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        if use_fallback:
            return get_fallback_response(prompt, system_prompt)
        raise HTTPException(
            status_code=503,
            detail="AI service unavailable"
        )

def get_fallback_response(prompt: str, system_prompt: str) -> str:
    """Generate intelligent fallback responses based on context"""
    
    # Detect if this is a chat/question
    if "question" in prompt.lower() or "explain" in prompt.lower() or "what" in prompt.lower():
        return """I understand you have a question, but I'm currently running in fallback mode without access to the AI service. 

To get full AI-powered responses, please:
1. Set your OPENROUTER_API_KEY in the .env file
2. Get a free API key from: https://openrouter.ai/keys
3. Restart the server

In the meantime, I can still help you with:
- Uploading and viewing PDFs
- Generating structured quiz questions (with basic templates)
- Tracking your progress
- Managing your study materials

What would you like to do?"""
    
    # Detect if this is quiz generation
    if "generate" in prompt.lower() and "quiz" in prompt.lower():
        return json.dumps([
            {
                "question": "What is the fundamental principle discussed in the material?",
                "question_type": "SAQ",
                "options": None,
                "correct_answer": "Please refer to the study material for the correct answer",
                "explanation": "This is a template question. Connect the AI service for personalized questions."
            }
        ])
    
    # Detect if this is YouTube recommendation
    if "youtube" in prompt.lower() or "video" in prompt.lower():
        topic = "this topic"
        if ":" in prompt:
            topic = prompt.split(":")[-1].strip()[:50]
        
        return json.dumps([
            {
                "title": f"Introduction to {topic}",
                "channel": "Khan Academy",
                "reason": "Clear and comprehensive explanations suitable for beginners"
            },
            {
                "title": f"Advanced concepts in {topic}",
                "channel": "Crash Course",
                "reason": "In-depth coverage with engaging visuals"
            },
            {
                "title": f"Practical applications of {topic}",
                "channel": "Physics Wallah",
                "reason": "Real-world examples and problem-solving techniques"
            }
        ])
    
    # Default fallback
    return "I'm currently operating in fallback mode. Please configure the OPENROUTER_API_KEY to enable full AI capabilities."

def find_citations(query: str, pages_text: Dict[str, str], top_k: int = 3) -> List[Dict]:
    """Simple keyword-based citation search"""
    citations = []
    query_words = set(query.lower().split())
    
    for page_num, text in pages_text.items():
        text_lower = text.lower()
        matches = sum(1 for word in query_words if word in text_lower)
        
        if matches > 0:
            sentences = text.split('.')
            best_sentence = ""
            max_matches = 0
            
            for sentence in sentences[:10]:
                sent_matches = sum(1 for word in query_words if word in sentence.lower())
                if sent_matches > max_matches:
                    max_matches = sent_matches
                    best_sentence = sentence.strip()
            
            if best_sentence:
                citations.append({
                    "page": int(page_num) if page_num.isdigit() else page_num,
                    "snippet": best_sentence[:200] + "..." if len(best_sentence) > 200 else best_sentence,
                    "relevance": matches
                })
    
    citations.sort(key=lambda x: x["relevance"], reverse=True)
    return citations[:top_k]

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="BeyondChats Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await connect_db()
    
    print("\n" + "="*60)
    print("🚀 BeyondChats Backend Starting...")
    print("="*60)
    print(f"🗄️  Database: {DATABASE_NAME}")
    print(f"📁 Upload Directory: {UPLOAD_DIR}")
    print(f"🤖 AI Model: {MODEL_NAME}")
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_key_here":
        print("⚠️  OpenRouter API Key: NOT SET")
        print("   → Running in FALLBACK MODE")
        print("   → Get free key: https://openrouter.ai/keys")
    else:
        print("✅ OpenRouter API Key: Configured")
    
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.get("/")
async def root():
    return {
        "message": "BeyondChats Backend API",
        "status": "running",
        "ai_configured": bool(OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_key_here")
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected" if db.client else "disconnected",
        "ai_service": "configured" if OPENROUTER_API_KEY else "fallback_mode"
    }

# ============================================================================
# PDF ROUTES 
# ============================================================================
@app.post("/api/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF"""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_size = 0
    pdf_id = str(ObjectId())
    file_path = os.path.join(UPLOAD_DIR, f"{pdf_id}.pdf")
    
    try:
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                file_size += len(chunk)
                if file_size > 50 * 1024 * 1024:
                    buffer.close()
                    os.remove(file_path)
                    raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
                buffer.write(chunk)
        
        print(f"📥 Saved PDF: {file.filename} ({file_size / 1024:.2f} KB)")
        
        pages_text = extract_text_from_pdf(file_path)
        
        if not pages_text:
            os.remove(file_path)
            raise HTTPException(status_code=422, detail="No text could be extracted from this PDF.")
        
        has_real_text = any("[Image-based page" not in text for text in pages_text.values())
        
        pdf_doc = {
            "_id": ObjectId(pdf_id),
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "total_pages": len(pages_text),
            "pages_text": pages_text,
            "is_image_based": not has_real_text,
            "uploaded_at": datetime.utcnow()
        }
        
        await get_database()["pdfs"].insert_one(pdf_doc)
        
        print(f"✅ Successfully processed PDF: {file.filename}")
        
        return {
            "pdf_id": pdf_id,
            "filename": file.filename,
            "total_pages": len(pages_text),
            "file_size": file_size,
            "is_image_based": not has_real_text,
            "message": "PDF uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"❌ PDF upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

@app.get("/api/pdf/list")
async def list_pdfs():
    """Get list of all uploaded PDFs"""
    pdfs = await get_database()["pdfs"].find({}).to_list(100)
    
    return {
        "pdfs": [
            {
                "pdf_id": str(pdf["_id"]),
                "filename": pdf["filename"],
                "total_pages": pdf["total_pages"],
                "file_size": pdf.get("file_size", 0),
                "is_image_based": pdf.get("is_image_based", False),
                "uploaded_at": pdf["uploaded_at"].isoformat()
            }
            for pdf in pdfs
        ]
    }

@app.get("/api/pdf/{pdf_id}")
async def get_pdf(pdf_id: str):
    """Get PDF file"""
    pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(pdf_id)})
    
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(pdf["file_path"], media_type="application/pdf", filename=pdf["filename"])

@app.get("/api/pdf/{pdf_id}/text")
async def get_pdf_text(pdf_id: str):
    """Get extracted text from PDF"""
    pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(pdf_id)})
    
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return {
        "pdf_id": pdf_id,
        "pages_text": pdf["pages_text"],
        "is_image_based": pdf.get("is_image_based", False)
    }

@app.delete("/api/pdf/{pdf_id}")
async def delete_pdf(pdf_id: str):
    """Delete a PDF"""
    pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(pdf_id)})
    
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    if os.path.exists(pdf["file_path"]):
        os.remove(pdf["file_path"])
    
    await get_database()["pdfs"].delete_one({"_id": ObjectId(pdf_id)})
    
    return {"message": "PDF deleted successfully"}

# ============================================================================
# QUIZ ROUTES
# ============================================================================
@app.post("/api/quiz/generate")
async def generate_quiz(request: QuizGenerateRequest):
    """Generate quiz questions from PDF"""
    try:
        if request.pdf_id:
            pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(request.pdf_id)})
            if not pdf:
                raise HTTPException(status_code=404, detail="PDF not found")
            
            if pdf.get("is_image_based", False):
                raise HTTPException(status_code=422, detail="Cannot generate quiz from image-based PDF.")
            
            all_text = " ".join(pdf["pages_text"].values())
            context = all_text[:4000]
        else:
            context = "General educational topics"
        
        prompt = f"""Based on the following content, generate quiz questions in STRICT JSON format:

Content: {context}

Generate exactly:
- {request.num_mcq} Multiple Choice Questions (MCQ) with 4 options each
- {request.num_saq} Short Answer Questions (SAQ)
- {request.num_laq} Long Answer Questions (LAQ)

RESPOND ONLY WITH A JSON ARRAY IN THIS EXACT FORMAT:
[
  {{
    "question": "What is X?",
    "question_type": "MCQ",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "correct_answer": "A) Option 1",
    "explanation": "Brief explanation"
  }},
  {{
    "question": "Explain Y",
    "question_type": "SAQ",
    "options": null,
    "correct_answer": "Expected answer",
    "explanation": "Brief explanation"
  }}
]

IMPORTANT: Return ONLY the JSON array, no other text."""

        system_prompt = "You are a quiz generator. Respond with ONLY valid JSON array, no markdown, no explanations."
        
        response = await call_llm(prompt, system_prompt, use_fallback=True)
        
        try:
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(line for line in lines if not line.startswith('```'))
                response = response.strip()
            
            # Find JSON array
            if not response.startswith('['):
                start = response.find('[')
                end = response.rfind(']') + 1
                if start != -1 and end > start:
                    response = response[start:end]
            
            questions_data = json.loads(response)
            
            # Validate and clean questions
            validated_questions = []
            for q in questions_data:
                try:
                    validated_questions.append(QuizQuestion(**q))
                except Exception as e:
                    print(f"⚠️  Skipping invalid question: {e}")
                    continue
            
            questions = validated_questions
            
        except Exception as e:
            print(f"⚠️  Failed to parse LLM response: {e}")
            print(f"Response was: {response[:500]}")
            
            # Fallback questions
            questions = [
                QuizQuestion(
                    question="What is the main topic discussed in the material?",
                    question_type="SAQ",
                    options=None,
                    correct_answer="Please refer to the study material",
                    explanation="This is a template question. Configure AI service for personalized questions."
                )
            ]
        
        if not questions:
            questions = [
                QuizQuestion(
                    question="What are the key concepts covered?",
                    question_type="SAQ",
                    options=None,
                    correct_answer="Refer to course material",
                    explanation="Template question - AI service needed for custom questions"
                )
            ]
        
        quiz_id = str(ObjectId())
        quiz_doc = {
            "_id": ObjectId(quiz_id),
            "pdf_id": request.pdf_id,
            "questions": [q.model_dump() for q in questions],
            "created_at": datetime.utcnow()
        }
        
        await get_database()["quizzes"].insert_one(quiz_doc)
        
        return {
            "quiz_id": quiz_id,
            "questions": questions,
            "total_questions": len(questions)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Quiz generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

@app.post("/api/quiz/submit")
async def submit_quiz(request: QuizSubmitRequest):
    """Submit quiz answers"""
    quiz = await get_database()["quizzes"].find_one({"_id": ObjectId(request.quiz_id)})
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = quiz["questions"]
    results = []
    correct_count = 0
    
    answer_map = {ans.question_index: ans.user_answer for ans in request.answers}
    
    for idx, question in enumerate(questions):
        user_answer = answer_map.get(idx, "")
        correct_answer = question["correct_answer"]
        
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_index": idx,
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question["explanation"]
        })
    
    score_percentage = (correct_count / len(questions)) * 100 if questions else 0
    
    attempt_doc = {
        "quiz_id": request.quiz_id,
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "score_percentage": score_percentage,
        "results": results,
        "submitted_at": datetime.utcnow()
    }
    
    await get_database()["attempts"].insert_one(attempt_doc)
    
    return {
        "quiz_id": request.quiz_id,
        "total_questions": len(questions),
        "correct_answers": correct_count,
        "score_percentage": score_percentage,
        "results": results
    }

# ============================================================================
# CHAT ROUTES 
# ============================================================================
@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with AI teacher"""
    try:
        print(f"💬 Chat request received: {request.message[:50]}...")
        
        # Get or create chat session
        if request.chat_id:
            chat_doc = await get_database()["chats"].find_one({"_id": ObjectId(request.chat_id)})
            if not chat_doc:
                raise HTTPException(status_code=404, detail="Chat not found")
            messages = chat_doc.get("messages", [])
            chat_id = request.chat_id
        else:
            chat_id = str(ObjectId())
            messages = []
        
        # Find citations if PDF is provided
        citations = []
        context = ""
        
        if request.pdf_id:
            try:
                pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(request.pdf_id)})
                if pdf:
                    pages_text = pdf["pages_text"]
                    citations = find_citations(request.message, pages_text, top_k=3)
                    
                    if citations:
                        context_parts = []
                        for c in citations:
                            context_parts.append(f"[Page {c['page']}]: {c['snippet']}")
                        context = "\n\n".join(context_parts)
                        print(f"📚 Found {len(citations)} relevant citations")
            except Exception as e:
                print(f"⚠️  Error finding citations: {e}")
        
        # Build prompt
        if context:
            prompt = f"""You are a helpful teacher. Answer the student's question based on these excerpts from their coursebook:

{context}

Student's question: {request.message}

Provide a clear, educational response. If the excerpts don't fully answer the question, use your knowledge but acknowledge this."""
        else:
            prompt = f"""You are a helpful teacher. Answer this student's question clearly and educationally:

Question: {request.message}

Provide a thorough, helpful response."""
        
        system_prompt = "You are a knowledgeable and patient teacher. Provide clear, educational responses that help students learn."
        
        # Get AI response
        response_text = await call_llm(prompt, system_prompt, use_fallback=True)
        
        print(f"✅ Chat response generated ({len(response_text)} chars)")
        
        # Save to database
        messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow()
        })
        
        messages.append({
            "role": "assistant",
            "content": response_text,
            "citations": citations,
            "timestamp": datetime.utcnow()
        })
        
        chat_doc = {
            "_id": ObjectId(chat_id),
            "pdf_id": request.pdf_id,
            "messages": messages,
            "last_message": request.message,
            "updated_at": datetime.utcnow()
        }
        
        if request.chat_id:
            await get_database()["chats"].update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": chat_doc}
            )
        else:
            chat_doc["created_at"] = datetime.utcnow()
            await get_database()["chats"].insert_one(chat_doc)
        
        return {
            "chat_id": chat_id,
            "message": response_text,
            "citations": citations
        }
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/chat/history")
async def get_chat_history():
    """Get all chat sessions"""
    try:
        chats = await get_database()["chats"].find({}).sort("updated_at", -1).to_list(100)
        
        return {
            "chats": [
                {
                    "chat_id": str(chat["_id"]),
                    "last_message": chat.get("last_message", ""),
                    "message_count": len(chat.get("messages", [])),
                    "updated_at": chat.get("updated_at", chat.get("created_at")).isoformat()
                }
                for chat in chats
            ]
        }
    except Exception as e:
        print(f"❌ Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{chat_id}")
async def get_chat(chat_id: str):
    """Get specific chat"""
    try:
        chat = await get_database()["chats"].find_one({"_id": ObjectId(chat_id)})
        
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {
            "chat_id": str(chat["_id"]),
            "messages": chat.get("messages", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error fetching chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat"""
    try:
        result = await get_database()["chats"].delete_one({"_id": ObjectId(chat_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {"message": "Chat deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROGRESS ROUTES
# ============================================================================
@app.get("/api/progress")
async def get_progress():
    """Get user progress statistics"""
    try:
        attempts = await get_database()["attempts"].find({}).sort("submitted_at", -1).to_list(100)
        
        if not attempts:
            return {
                "total_quizzes": 0,
                "total_questions_answered": 0,
                "overall_score": 0,
                "recent_attempts": [],
                "strengths": [],
                "weaknesses": []
            }
        
        total_questions = sum(a["total_questions"] for a in attempts)
        total_score = sum(a["score_percentage"] for a in attempts)
        avg_score = total_score / len(attempts) if attempts else 0
        
        # Get recent attempts
        recent = attempts[:10]
        recent_attempts = [
            {
                "date": a["submitted_at"].isoformat(),
                "score": a["score_percentage"],
                "questions": a["total_questions"]
            }
            for a in recent
        ]
        
        # Analyze strengths and weaknesses (simplified)
        high_scores = [a for a in attempts if a["score_percentage"] >= 80]
        low_scores = [a for a in attempts if a["score_percentage"] < 60]
        
        strengths = []
        weaknesses = []
        
        if high_scores:
            strengths.append(f"Consistently scoring well ({len(high_scores)} quizzes above 80%)")
        
        if low_scores:
            weaknesses.append(f"Some challenging areas ({len(low_scores)} quizzes below 60%)")
        
        if avg_score >= 70:
            strengths.append("Strong overall performance")
        
        return {
            "total_quizzes": len(attempts),
            "total_questions_answered": total_questions,
            "overall_score": round(avg_score, 1),
            "recent_attempts": recent_attempts,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
        
    except Exception as e:
        print(f"❌ Progress error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# YOUTUBE RECOMMENDATION ROUTES
# ============================================================================
@app.post("/api/recommend/youtube")
async def recommend_youtube(request: YouTubeRequest):
    """Get YouTube video recommendations"""
    try:
        context = ""
        if request.pdf_id:
            pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(request.pdf_id)})
            if pdf:
                all_text = " ".join(pdf["pages_text"].values())
                context = all_text[:2000]
        
        prompt = f"""Recommend 3 educational YouTube videos for the topic: "{request.topic}"

{f"Context from coursebook: {context}" if context else ""}

Provide recommendations in this EXACT JSON format:
[
  {{
    "title": "Video title",
    "channel": "Channel name",
    "reason": "Why this video is recommended"
  }}
]

Focus on:
- Educational channels (Khan Academy, Crash Course, etc.)
- Clear explanations
- Relevance to the topic

RESPOND WITH ONLY THE JSON ARRAY, NO OTHER TEXT."""

        system_prompt = "You are an educational content curator. Respond with ONLY valid JSON array, no markdown, no explanations."
        
        response = await call_llm(prompt, system_prompt, use_fallback=True)
        
        try:
            # Clean response
            response = response.strip()
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(line for line in lines if not line.startswith('```'))
                response = response.strip()
            
            if not response.startswith('['):
                start = response.find('[')
                end = response.rfind(']') + 1
                if start != -1 and end > start:
                    response = response[start:end]
            
            recommendations = json.loads(response)
            
            # Validate
            if not isinstance(recommendations, list):
                raise ValueError("Response is not a list")
            
            # Ensure we have at least some recommendations
            if len(recommendations) == 0:
                raise ValueError("No recommendations in response")
            
        except Exception as e:
            print(f"⚠️  Failed to parse recommendations: {e}")
            print(f"Response was: {response[:500]}")
            
            # Fallback recommendations
            recommendations = [
                {
                    "title": f"Introduction to {request.topic}",
                    "channel": "Khan Academy",
                    "reason": "Comprehensive introduction with clear explanations"
                },
                {
                    "title": f"{request.topic} - Complete Guide",
                    "channel": "Crash Course",
                    "reason": "In-depth coverage with visual aids"
                },
                {
                    "title": f"Understanding {request.topic}",
                    "channel": "3Blue1Brown",
                    "reason": "Visual and intuitive explanations"
                }
            ]
        
        return {
            "topic": request.topic,
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"❌ YouTube recommendation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUN SERVER
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting BeyondChats Server...")
    print("="*60)
    print(f"📡 API: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"🔧 Health: http://localhost:8000/health")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
