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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your_key_here")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-3.5-turbo"

Use absolute path and handle Render environment
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/uploads")
if not os.path.isabs(UPLOAD_DIR):
    UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)

# Create upload directory
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
print(f"📁 Upload directory: {UPLOAD_DIR}")

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
                if text.strip():  # Only add if there's actual text
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
    
    # Try pdfplumber first (best for most PDFs)
    pages_text = extract_text_with_pdfplumber(pdf_path)
    if pages_text:
        print(f"✅ Extracted {len(pages_text)} pages using pdfplumber")
        return pages_text
    
    # Fallback to PyMuPDF (good for scanned PDFs)
    print("📄 Trying PyMuPDF...")
    pages_text = extract_text_with_pymupdf(pdf_path)
    if pages_text:
        print(f"✅ Extracted {len(pages_text)} pages using PyMuPDF")
        return pages_text
    
    # Final fallback to PyPDF2
    print("📄 Trying PyPDF2...")
    pages_text = extract_text_with_pypdf2(pdf_path)
    if pages_text:
        print(f"✅ Extracted {len(pages_text)} pages using PyPDF2")
        return pages_text
    
    # If all methods fail, check if PDF has pages but no text (image-based PDF)
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        
        if total_pages > 0:
            print(f"⚠️  PDF has {total_pages} pages but no extractable text (might be image-based)")
            # Return empty pages to indicate structure exists
            return {str(i + 1): "[Image-based page - OCR needed]" for i in range(total_pages)}
    except:
        pass
    
    raise HTTPException(
        status_code=422, 
        detail="Unable to extract text from PDF. The file might be corrupted, password-protected, or image-based. Please try a different PDF or use OCR."
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

async def call_llm(prompt: str, system_prompt: str = "You are a helpful AI assistant.") -> str:
    """Call OpenRouter API (GPT-3.5) using httpx"""
    try:
        # Check if API key is set
        if OPENROUTER_API_KEY == "your_key_here" or not OPENROUTER_API_KEY:
            print("⚠️  Warning: OpenRouter API key not set. Using fallback responses.")
            return "This is a fallback response. Please set OPENROUTER_API_KEY environment variable."
        
        # Direct HTTP request to OpenRouter
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                    "temperature": 0.7
                }
            )
            
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
    except httpx.HTTPStatusError as e:
        print(f"❌ LLM API HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return f"AI service error: {e.response.status_code}. Please check your API key."
    except httpx.TimeoutException:
        print("❌ LLM API Timeout")
        return "The AI service is taking too long to respond. Please try again."
    except Exception as e:
        print(f"❌ LLM API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"I'm currently unable to connect to the AI service. Please try again later."

def find_citations(query: str, pages_text: Dict[str, str], top_k: int = 3) -> List[Dict]:
    """Simple keyword-based citation search"""
    citations = []
    query_words = set(query.lower().split())
    
    for page_num, text in pages_text.items():
        text_lower = text.lower()
        # Count matching words
        matches = sum(1 for word in query_words if word in text_lower)
        
        if matches > 0:
            # Extract snippet
            sentences = text.split('.')
            best_sentence = ""
            max_matches = 0
            
            for sentence in sentences[:10]:  # Check first 10 sentences
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
    
    # Sort by relevance and return top_k
    citations.sort(key=lambda x: x["relevance"], reverse=True)
    return citations[:top_k]

# ============================================================================
# FASTAPI APP
# ============================================================================
app = FastAPI(title="BeyondChats Backend", version="1.0.0")

# CORS middleware
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
    
    # Print configuration status (production-safe)
    print("\n" + "="*60)
    print("🚀 BeyondChats Backend Starting...")
    print("="*60)
    print(f"🗄️  Database: {DATABASE_NAME}")
    print(f"📁 Upload Directory: {UPLOAD_DIR}")
    print(f"✅ Upload Directory Exists: {os.path.isdir(UPLOAD_DIR)}")
    print(f"✅ Upload Directory Writable: {os.access(UPLOAD_DIR, os.W_OK)}")
    
    # Check API key without exposing it
    if OPENROUTER_API_KEY == "your_key_here" or not OPENROUTER_API_KEY:
        print("⚠️  OpenRouter API Key: NOT SET")
        print("   ↓ Set OPENROUTER_API_KEY in .env file or environment variable")
        print("   ↓ Get your key at: https://openrouter.ai/keys")
    else:
        print("✅ OpenRouter API Key: Configured")
    
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# ============================================================================
# PDF ROUTES 
# ============================================================================
@app.post("/api/pdf/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF with improved extraction"""
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Validate file size (max 50MB)
    file_size = 0
    pdf_id = str(ObjectId())
    file_path = os.path.join(UPLOAD_DIR, f"{pdf_id}.pdf")
    
    try:
        # Save file with size check
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # Read 1MB at a time
                file_size += len(chunk)
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    buffer.close()
                    os.remove(file_path)
                    raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB")
                buffer.write(chunk)
        
        print(f"📥 Saved PDF: {file.filename} ({file_size / 1024:.2f} KB)")
        print(f"📍 File path: {file_path}")
        
        # Extract text with improved method
        pages_text = extract_text_from_pdf(file_path)
        
        if not pages_text:
            os.remove(file_path)
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from this PDF. It might be image-based or corrupted."
            )
        
        # Check if it's an image-based PDF
        has_real_text = any(
            "[Image-based page" not in text 
            for text in pages_text.values()
        )
        
        # Store in MongoDB
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
            "message": "PDF uploaded and processed successfully" if has_real_text else "PDF uploaded but appears to be image-based. OCR might be needed for best results."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup on error
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
                "file_exists": os.path.exists(pdf.get("file_path", "")),
                "uploaded_at": pdf["uploaded_at"].isoformat()
            }
            for pdf in pdfs
        ]
    }

@app.get("/api/pdf/{pdf_id}")
async def get_pdf(pdf_id: str):
    """Get PDF file (Proper error handling and path validation)"""
    try:
        pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(pdf_id)})
        
        if not pdf:
            raise HTTPException(status_code=404, detail="PDF not found in database")
        
        file_path = pdf.get("file_path")
        
        # FIX: Check if file exists
        if not file_path or not os.path.exists(file_path):
            print(f"❌ PDF file not found: {file_path}")
            raise HTTPException(
                status_code=404, 
                detail=f"PDF file not found on disk. File path: {file_path}"
            )
        
        # FIX: Verify file is readable
        if not os.access(file_path, os.R_OK):
            raise HTTPException(status_code=403, detail="PDF file is not readable")
        
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=pdf.get("filename", "document.pdf")
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error retrieving PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving PDF: {str(e)}")

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
    
    # Delete file
    file_path = pdf.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"✅ Deleted file: {file_path}")
        except Exception as e:
            print(f"⚠️  Could not delete file {file_path}: {str(e)}")
    
    # Delete from database
    await get_database()["pdfs"].delete_one({"_id": ObjectId(pdf_id)})
    
    return {"message": "PDF deleted successfully"}

# ============================================================================
# QUIZ ROUTES
# ============================================================================
@app.post("/api/quiz/generate")
async def generate_quiz(request: QuizGenerateRequest):
    """Generate quiz questions from PDF"""
    try:
        # Get PDF content
        if request.pdf_id:
            pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(request.pdf_id)})
            if not pdf:
                raise HTTPException(status_code=404, detail="PDF not found")
            
            # Check if image-based
            if pdf.get("is_image_based", False):
                raise HTTPException(
                    status_code=422,
                    detail="Cannot generate quiz from image-based PDF. Please use a text-based PDF."
                )
            
            # Combine all pages text
            all_text = " ".join(pdf["pages_text"].values())
            context = all_text[:4000]  # Limit context
        else:
            context = "General Physics topics from Class XI NCERT"
        
        # Generate questions using LLM
        prompt = f"""Based on the following content, generate quiz questions:

Content: {context}

Generate exactly:
- {request.num_mcq} Multiple Choice Questions (MCQ) with 4 options each
- {request.num_saq} Short Answer Questions (SAQ)
- {request.num_laq} Long Answer Questions (LAQ)

Format your response as a JSON array with this structure:
[
  {{
    "question": "question text",
    "question_type": "MCQ|SAQ|LAQ",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct_answer": "correct answer text",
    "explanation": "detailed explanation"
  }}
]

Important:
- For MCQ, always include 4 options in the array
- For SAQ and LAQ, set options to null or empty array
- Ensure valid JSON format
- Questions should test understanding of the content"""

        system_prompt = "You are an expert teacher creating educational quiz questions. Always respond with valid JSON only, no additional text."
        
        response = await call_llm(prompt, system_prompt)
        
        try:
            # Try to extract JSON from response if it contains extra text
            response = response.strip()
            if not response.startswith('['):
                # Try to find JSON array in response
                start = response.find('[')
                end = response.rfind(']') + 1
                if start != -1 and end > start:
                    response = response[start:end]
            
            # Parse JSON response
            questions_data = json.loads(response)
            questions = [QuizQuestion(**q) for q in questions_data]
        except Exception as parse_error:
            print(f"⚠️  Failed to parse LLM response: {parse_error}")
            print(f"Response was: {response[:500]}")
            # Fallback if parsing fails
            questions = [
                QuizQuestion(
                    question="What is the SI unit of force?",
                    question_type="MCQ",
                    options=["A) Newton", "B) Joule", "C) Watt", "D) Pascal"],
                    correct_answer="A) Newton",
                    explanation="The SI unit of force is Newton (N), named after Sir Isaac Newton."
                ),
                QuizQuestion(
                    question="Explain Newton's First Law of Motion.",
                    question_type="SAQ",
                    options=None,
                    correct_answer="An object at rest stays at rest and an object in motion stays in motion unless acted upon by an external force.",
                    explanation="This is also known as the law of inertia."
                ),
                QuizQuestion(
                    question="Describe the relationship between force, mass, and acceleration.",
                    question_type="LAQ",
                    options=None,
                    correct_answer="Force equals mass times acceleration (F=ma). This means that the force applied to an object is directly proportional to its mass and acceleration.",
                    explanation="This is Newton's Second Law of Motion."
                )
            ]
        
        # Store quiz in database
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
    """Submit quiz answers and get results"""
    # Get quiz
    quiz = await get_database()["quizzes"].find_one({"_id": ObjectId(request.quiz_id)})
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    questions = quiz["questions"]
    results = []
    correct_count = 0
    
    # Create answer map
    answer_map = {ans.question_index: ans.user_answer for ans in request.answers}
    
    # Evaluate answers
    for idx, question in enumerate(questions):
        user_answer = answer_map.get(idx, "")
        correct_answer = question["correct_answer"]
        
        # Simple matching (case-insensitive)
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
    
    # Store attempt
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
        # Get or create chat
        if request.chat_id:
            chat_doc = await get_database()["chats"].find_one({"_id": ObjectId(request.chat_id)})
            if not chat_doc:
                raise HTTPException(status_code=404, detail="Chat not found")
            messages = chat_doc.get("messages", [])
        else:
            chat_id = str(ObjectId())
            messages = []
            chat_doc = {
                "_id": ObjectId(chat_id),
                "pdf_id": request.pdf_id,
                "messages": [],
                "created_at": datetime.utcnow()
            }
            request.chat_id = chat_id
        
        # Get PDF context if provided
        citations = []
        context = ""
        
        if request.pdf_id:
            pdf = await get_database()["pdfs"].find_one({"_id": ObjectId(request.pdf_id)})
            if pdf:
                pages_text = pdf["pages_text"]
                citations = find_citations(request.message, pages_text)
                
                if citations:
                    context = "\n\n".join([
                        f"[Page {c['page']}]: {c['snippet']}" 
                        for c in citations
                    ])
        
        # Build prompt
        if context:
            prompt = f"""Based on the following excerpts from the textbook, answer the student's question:

{context}

Student's question: {request.message}

Provide a helpful, educational response. If the excerpts are relevant, reference them naturally."""
        else:
            prompt = f"Student's question: {request.message}\n\nProvide a helpful, educational response as a teacher."
        
        system_prompt = "You are a knowledgeable and patient teacher helping students learn. Be clear, encouraging, and educational."
        
        response_text = await call_llm(prompt, system_prompt)
        
        # Add messages
        messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow()
        })
        
        messages.append({
            "role": "assistant",
            "content": response_text,
            "citations": citations if citations else None,
            "timestamp": datetime.utcnow()
        })
        
        # Update chat
        await get_database()["chats"].update_one(
            {"_id": ObjectId(request.chat_id)},
            {"$set": {"messages": messages, "updated_at": datetime.utcnow()}},
            upsert=True
        )
        
        return {
            "chat_id": request.chat_id,
            "message": response_text,
            "citations": citations if citations else None
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/chat/history")
async def get_chat_history():
    """Get all chat sessions"""
    chats = await get_database()["chats"].find({}).sort("_id", -1).to_list(50)
    
    return {
        "chats": [
            {
                "chat_id": str(chat["_id"]),
                "pdf_id": chat.get("pdf_id"),
                "message_count": len(chat.get("messages", [])),
                "last_message": chat["messages"][-1]["content"][:100] if chat.get("messages") else "",
                "created_at": chat.get("created_at", datetime.utcnow()).isoformat() if isinstance(chat.get("created_at"), datetime) else datetime.utcnow().isoformat(),
                "updated_at": chat.get("updated_at", chat.get("created_at", datetime.utcnow())).isoformat() if isinstance(chat.get("updated_at", chat.get("created_at")), datetime) else datetime.utcnow().isoformat()
            }
            for chat in chats
        ]
    }

@app.get("/api/chat/{chat_id}")
async def get_chat(chat_id: str):
    """Get specific chat with all messages"""
    try:
        chat = await get_database()["chats"].find_one({"_id": ObjectId(chat_id)})
        
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Ensure messages have proper structure
        messages = chat.get("messages", [])
        formatted_messages = []
        
        for msg in messages:
            formatted_msg = {
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", datetime.utcnow()).isoformat() if isinstance(msg.get("timestamp"), datetime) else datetime.utcnow().isoformat()
            }
            if "citations" in msg and msg["citations"]:
                formatted_msg["citations"] = msg["citations"]
            formatted_messages.append(formatted_msg)
        
        return {
            "chat_id": str(chat["_id"]),
            "pdf_id": chat.get("pdf_id"),
            "messages": formatted_messages
        }
    except Exception as e:
        print(f"❌ Error fetching chat: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat: {str(e)}")

# ============================================================================
# PROGRESS ROUTES
# ============================================================================
@app.get("/api/progress")
async def get_progress():
    """Get user's learning progress"""
    attempts = await get_database()["attempts"].find({}).to_list(100)
    
    if not attempts:
        return {
            "total_quizzes": 0,
            "total_questions_answered": 0,
            "overall_score": 0,
            "strengths": [],
            "weaknesses": [],
            "recent_attempts": []
        }
    
    total_questions = sum(a["total_questions"] for a in attempts)
    total_correct = sum(a["correct_answers"] for a in attempts)
    overall_score = (total_correct / total_questions * 100) if total_questions > 0 else 0
    
    # Analyze strengths/weaknesses (simplified)
    strengths = ["Problem Solving"] if overall_score > 70 else []
    weaknesses = ["Conceptual Understanding"] if overall_score < 60 else []
    
    recent_attempts = [
        {
            "quiz_id": str(a["quiz_id"]),
            "score": a["score_percentage"],
            "date": a["submitted_at"].isoformat()
        }
        for a in sorted(attempts, key=lambda x: x["submitted_at"], reverse=True)[:5]
    ]
    
    return {
        "total_quizzes": len(attempts),
        "total_questions_answered": total_questions,
        "overall_score": round(overall_score, 2),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recent_attempts": recent_attempts
    }

# ============================================================================
# YOUTUBE RECOMMENDATION ROUTES
# ============================================================================
@app.post("/api/recommend/youtube")
async def recommend_youtube(request: YouTubeRequest):
    """Recommend YouTube videos for a topic"""
    try:
        prompt = f"""Suggest 3 educational YouTube video titles and channels for learning about: {request.topic}

Format as JSON array:
[
  {{"title": "video title", "channel": "channel name", "reason": "why this is helpful"}},
  {{"title": "video title", "channel": "channel name", "reason": "why this is helpful"}},
  {{"title": "video title", "channel": "channel name", "reason": "why this is helpful"}}
]

Only respond with the JSON array, no additional text."""

        system_prompt = "You are an educational content curator. Suggest real, popular educational YouTube channels. Respond with valid JSON only."
        
        response = await call_llm(prompt, system_prompt)
        
        try:
            # Try to extract JSON from response
            response = response.strip()
            if not response.startswith('['):
                start = response.find('[')
                end = response.rfind(']') + 1
                if start != -1 and end > start:
                    response = response[start:end]
            
            recommendations = json.loads(response)
        except Exception as parse_error:
            print(f"⚠️  Failed to parse YouTube recommendations: {parse_error}")
            # Fallback recommendations
            recommendations = [
                {
                    "title": f"Introduction to {request.topic}",
                    "channel": "Khan Academy",
                    "reason": "Clear explanations with visual aids"
                },
                {
                    "title": f"{request.topic} - Complete Guide",
                    "channel": "Physics Wallah",
                    "reason": "In-depth coverage with examples"
                },
                {
                    "title": f"Understanding {request.topic}",
                    "channel": "Vedantu",
                    "reason": "Student-friendly explanations"
                }
            ]
        
        return {"recommendations": recommendations}
    except Exception as e:
        print(f"❌ YouTube recommendation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"YouTube recommendation failed: {str(e)}")

# ============================================================================
# HEALTH CHECK
# ============================================================================
@app.get("/")
async def root():
    return {"message": "BeyondChats Backend API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
