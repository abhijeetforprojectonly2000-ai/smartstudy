# SmartStudy - AI-Powered Learning Assistant 🎓

A modern, full-stack web application that helps school students learn smarter using AI-powered quizzes, chat assistance, and progress tracking. Built with React, FastAPI, and MongoDB.

## 🌟 Live Demo

- **Frontend:** smartstudy-steel.vercel.app
- **Backend API:** https://smartstudy-8q14.onrender.com/
  

## ⚠️ Important: First-Time Usage

Before testing the frontend, please follow these steps:

1. **Wake up the backend server first** by visiting: `https://smartstudy-8q14.onrender.com/`
   - Render free tier puts inactive services to sleep after 15 minutes
   - First request takes 30-50 seconds to wake up the server (cold start)
   - You'll see `{"status": "running"}` when it's ready

2. **Then access the frontend:** `smartstudy-steel.vercel.app`

3. **PDF Upload Notice:**
   - First PDF upload may take 1-2 minutes due to:
     - Cold start of backend service
     - PDF processing and text extraction
     - Database storage
   - Subsequent uploads are faster (10-30 seconds)
   - Please be patient and don't refresh the page during upload

4. **Known Limitation - Memory Constraints:**
   - ⚠️ **Render free tier has 512MB RAM limit**
   - Backend may crash with "Out of Memory" error during heavy usage
   - This can happen when:
     - Processing large PDFs (>20MB)
     - Multiple concurrent users uploading PDFs
     - Running intensive AI operations
   - If this occurs, the service will automatically restart (30-50 seconds)
   - For testing, please use the provided sample PDFs from the repository
     
5. **Testing Files**
    - Uploaded a zipfile of the documents to be tested for this app
    - **Please use ONLY the provided sample PDFs** from the repository for testing
    - Uploading additional or larger PDFs may cause memory errors on free tier

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup Instructions](#-setup-instructions)
- [Environment Variables](#-environment-variables)
- [Development Workflow](#-development-workflow)
- [Deployment](#-deployment)
- [Implementation Details](#-implementation-details)
- [Trade-offs & Decisions](#-trade-offs--decisions)
- [What's Completed](#-whats-completed)
- [Future Improvements](#-future-improvements)
- [LLM Usage](#-llm-usage)
- [Testing](#-testing)
- [Debugging Tips](#-debugging-tips)

## ✨ Features

### Core Features

**Source Selector**
- Upload custom PDF coursebooks
- View all uploaded PDFs
- Select specific PDF or "All PDFs" mode
- Pre-seeded with NCERT Class XI Physics PDFs

**PDF Viewer**
- Built-in PDF viewer with page navigation
- Split-view with document library
- Download functionality
- Responsive design for mobile

**Quiz Generator Engine**
- AI-generated MCQs, SAQs, and LAQs
- Customizable question distribution
- Real-time scoring and feedback
- Detailed explanations for each answer
- Option to generate new quizzes
- Progress tracking per quiz

**Progress Tracking**
- Comprehensive dashboard with analytics
- Performance trends visualization
- Strengths and weaknesses analysis
- Quiz history tracking
- Overall score calculation

### Advanced Features

**Chat UI (ChatGPT-inspired)**
- Clean, modern chat interface
- Left sidebar with chat history
- New chat creation
- Context-aware conversations
- PDF-based Q&A support
- Mobile responsive

**RAG Answers with Citations**
- PDF text extraction and chunking
- Citation-based responses
- Page number references
- Snippet quotes from source material
- Relevance-based citation ranking

**YouTube Video Recommender**
- Topic-based video recommendations
- AI-curated educational content
- Channel and reason for recommendation
- Integration with course material

## 🛠 Tech Stack

### Frontend
- **React 18.2** - UI library
- **React Router 6** - Client-side routing
- **TailwindCSS 3.4** - Styling framework
- **Recharts 2.10** - Data visualization
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Vite 5** - Build tool

### Backend
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **PDFPlumber** - Primary PDF text extraction
- **PyPDF2** - Fallback PDF extraction
- **PyMuPDF (fitz)** - Alternative PDF extraction
- **httpx** - Async HTTP client
- **OpenRouter API** - LLM integration (GPT-3.5)
- **Pydantic** - Data validation

### Database
- **MongoDB Atlas** - Cloud database

### Deployment
- **Vercel** - Frontend hosting
- **Render** - Backend hosting (Free tier with cold starts and 512MB RAM limit)

## 📁 Project Structure

```
smartstudy/
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main app component with routing
│   │   ├── components.jsx       # All page components
│   │   ├── api.js              # API service layer
│   │   ├── utils.js            # Utility functions
│   │   ├── main.jsx            # App entry point
│   │   └── styles.css          # Global styles
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── uploads/               # PDF storage directory
├── .env.example
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- MongoDB Atlas account (or local MongoDB)
- OpenRouter API key (for LLM features)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/smartstudy.git
cd smartstudy
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials:
# - MONGODB_URI (from MongoDB Atlas)
# - OPENROUTER_API_KEY (from openrouter.ai)
# - DATABASE_NAME

# Run the backend with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

**Note:** You can also run with: `python main.py` which uses uvicorn internally.

### 3. Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with backend URL
# VITE_API_URL=http://localhost:8000

# Run the frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### 4. Access the Application

Open your browser and navigate to `http://localhost:3000`

## 🔐 Environment Variables

### Backend (.env)

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=smartstudy_db
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**How to get these:**

**MongoDB URI:**
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Add your IP to whitelist (or allow all: 0.0.0.0/0)
4. Create database user
5. Get connection string from "Connect" → "Connect your application"

**OpenRouter API Key:**
1. Sign up at [OpenRouter.ai](https://openrouter.ai)
2. Go to Keys section
3. Create new API key
4. Add credits (requires payment)

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

For production: `VITE_API_URL=https://your-backend.render.com`

## 💻 Development Workflow

### Running Backend in Development

**Method 1: Using Uvicorn directly (Recommended for development)**

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Method 2: Using Python (runs uvicorn internally)**

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Uvicorn Options:**
- `--reload` - Auto-reload on code changes (development only)
- `--host 0.0.0.0` - Allow external connections
- `--port 8000` - Port number
- `--workers 4` - Multiple worker processes (production)

### Running Frontend in Development

```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
```bash
# Production-ready command
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Connect repository to Vercel
3. Configure build settings:
   - **Framework:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Root Directory:** `frontend`
4. Add environment variable:
   - `VITE_API_URL=https://your-backend.render.com`
5. Deploy

### Backend (Render)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Configure:
   - **Environment:** Python 3
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `cd backend&&uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `MONGODB_URI`
   - `OPENROUTER_API_KEY`
   - `DATABASE_NAME`
6. Deploy

**Important Notes:**
- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-50 seconds (cold start)
- **Free tier has 512MB RAM limit** - may crash with "Out of Memory" error
- For production, consider upgrading to a paid plan to avoid cold starts and memory issues
- Render automatically sets the `PORT` environment variable

### Testing the Deployed Application

**Step 1: Wake up the backend**
```bash
# Visit the health check endpoint first
curl https://your-backend.render.com/health

# Or open in browser:
https://your-backend.render.com/health
```
Wait for `{"status": "healthy"}` response (30-50 seconds on cold start)

**Step 2: Access the frontend**
```
https://your-frontend.vercel.app
```

**Step 3: Upload your first PDF**
- Be patient during first upload (1-2 minutes)
- Don't refresh the page
- Subsequent uploads are faster
- **Use only the provided sample PDFs** to avoid memory issues

## 🏗 Implementation Details

### PDF Processing Pipeline
1. **Upload:** User uploads PDF via drag-drop or file selector
2. **Storage:** File saved to `/uploads` with unique ObjectId
3. **Extraction:** Multi-method text extraction (PDFPlumber → PyMuPDF → PyPDF2)
4. **Database:** Metadata and text stored in MongoDB
5. **Retrieval:** Citations found using keyword matching

**Current Upload Time:** 30-120 seconds (depending on cold start and PDF size)

**Text Extraction Strategy:**
- **Primary Method:** PDFPlumber (best for most text-based PDFs)
- **Fallback 1:** PyMuPDF/fitz (good for scanned PDFs and complex layouts)
- **Fallback 2:** PyPDF2 (final fallback for problematic PDFs)
- **Image Detection:** Automatically detects image-based PDFs that may need OCR

### Quiz Generation Flow
1. **Context Building:** Extract relevant text from PDF (4000 char limit)
2. **LLM Prompt:** Structured JSON prompt with question requirements
3. **Parsing:** Parse JSON response into QuizQuestion objects
4. **Fallback:** Hardcoded questions if LLM fails
5. **Storage:** Quiz stored in MongoDB with unique ID
6. **Evaluation:** Answer matching and scoring logic

### RAG Implementation
1. **Text Chunking:** Split PDF text into manageable chunks
2. **Query Processing:** Extract keywords from user query
3. **Citation Search:** Find relevant pages using keyword matching
4. **Snippet Extraction:** Extract relevant sentences from pages
5. **Ranking:** Sort by relevance score
6. **Response:** LLM generates answer with citations

### Chat Architecture
1. **Session Management:** Each chat has unique ID
2. **Message Storage:** All messages stored in MongoDB
3. **Context Window:** Recent messages sent to LLM
4. **Citations:** Relevant PDF snippets included in context
5. **Streaming:** Responses displayed in real-time

## 🎯 Trade-offs & Decisions

### 1. Vector Database vs Keyword Search
- **Decision:** Used keyword-based citation search
- **Reason:** Faster implementation, no need for embedding models
- **Trade-off:** Less semantic understanding, but adequate for MVP
- **Future:** Can upgrade to Pinecone/Weaviate for better relevance

### 2. LLM Provider Choice
- **Decision:** OpenRouter API (GPT-3.5)
- **Reason:** Cost-effective, reliable, good quality
- **Trade-off:** External dependency, requires API key
- **Alternative:** Could use Ollama for local LLMs

### 3. State Management
- **Decision:** React useState/useEffect (no Redux)
- **Reason:** Simple app, component-level state sufficient
- **Trade-off:** May need refactoring if app grows
- **Future:** Consider Zustand or Context API for global state

### 4. PDF Storage
- **Decision:** Local file system + MongoDB metadata
- **Reason:** Simple, no S3 costs for MVP
- **Trade-off:** Not scalable for production, consumes server memory
- **Future:** Migrate to S3/CloudFlare R2

### 5. Authentication
- **Decision:** No authentication in MVP
- **Reason:** Focus on core features first
- **Trade-off:** Single-user app
- **Future:** Add Auth0 or JWT-based auth

### 6. Caching
- **Decision:** No caching layer
- **Reason:** Simple architecture
- **Trade-off:** Repeated LLM calls cost money
- **Future:** Add Redis for response caching

### 7. Server Choice
- **Decision:** Uvicorn ASGI server
- **Reason:** FastAPI's recommended server, async support, excellent performance
- **Benefit:** Handles concurrent requests efficiently, perfect for async operations

### 8. Hosting Provider
- **Decision:** Render free tier for backend
- **Reason:** Zero cost, easy deployment, good for MVP
- **Trade-off:** Cold starts after 15 minutes + **512MB RAM limit causing crashes**
- **Future:** Upgrade to paid tier ($7-25/month) for always-on service and 2GB+ RAM

### 9. PDF Extraction Strategy
- **Decision:** Multi-method fallback approach (PDFPlumber → PyMuPDF → PyPDF2)
- **Reason:** Maximize compatibility with different PDF types
- **Benefit:** Higher success rate for text extraction
- **Trade-off:** Slightly more complex error handling

## ✅ What's Completed

### Core Features
- ✅ Source selector with PDF upload
- ✅ PDF viewer with navigation
- ✅ Multi-method PDF text extraction (PDFPlumber, PyMuPDF, PyPDF2)
- ✅ Image-based PDF detection
- ✅ Quiz generator (MCQ, SAQ, LAQ)
- ✅ Quiz scoring and explanations
- ✅ Progress tracking dashboard
- ✅ Analytics and visualizations

### Advanced Features
- ✅ Chat UI with conversation history
- ✅ RAG answers with citations
- ✅ YouTube video recommendations
- ✅ Mobile responsive design
- ✅ Modern, polished UI

### Additional Features
- ✅ Real-time PDF preview
- ✅ Quiz history tracking
- ✅ Performance trends chart
- ✅ Strengths/weaknesses analysis
- ✅ Dark mode compatible design
- ✅ Loading states and error handling
- ✅ Toast notifications
- ✅ Smooth animations
- ✅ Robust PDF processing with multiple extraction methods

## 🚀 Future Improvements

### 1. Performance Optimization - Upload Speed

**Current Issues:**
- PDF upload takes 30-120 seconds due to:
  - Render cold start (30-50 seconds)
  - Synchronous PDF text extraction
  - Large file processing
  - Network latency

**Proposed Solutions:**

**A. Upgrade Hosting**
- Migrate to Render paid tier ($7-25/month) - eliminates cold starts
- Or use Railway, Fly.io, or AWS Lambda with warmer instances
- Expected improvement: Reduce upload time by 50-70%

**B. Background Processing**
- Implement async PDF processing with Celery/RQ
- Save file immediately and return response
- Process text extraction in background
- Client polls for completion status
- Expected improvement: Instant response (1-2 seconds), processing in background

**C. Chunked Upload**
- Split large files into chunks (1MB each)
- Upload chunks progressively
- Better progress feedback
- Resumable uploads
- Expected improvement: Better UX, resumable uploads

**D. Optimize PDF Processing**
- Use faster PDF library combinations
- Parallel page processing with asyncio
- Process multiple pages simultaneously
- Expected improvement: 40-60% faster extraction

**E. CDN/Edge Storage**
- Use Cloudflare R2 or AWS S3 for file storage
- Cloudflare Workers for edge computing
- Process PDFs closer to user location
- Expected improvement: 30-50% faster uploads

**F. Progressive Enhancement**
- Show PDF preview while processing text
- Display upload progress in real-time
- Enable quiz generation before full extraction completes
- Expected improvement: Better UX, perceived performance increase

**G. Caching & Deduplication**
- Check if PDF already exists (hash-based)
- Skip processing for duplicate uploads
- Store frequently accessed PDFs in cache
- Expected improvement: Instant for duplicate uploads

**Implementation Priority:**
1. ✅ Background processing (biggest impact)
2. ✅ Upgrade to paid hosting (eliminates cold starts)
3. ✅ Optimize PDF extraction library
4. Progressive enhancement (better UX)
5. CDN storage (scalability)
6. Chunked upload (large files)
7. Caching (duplicate detection)

### 2. Memory Management & Hosting Upgrade

**Current Critical Issue:**
- ⚠️ **Render free tier crashes with "Out of Memory (512MB)" error**
- Happens during:
  - Large PDF processing (>20MB)
  - Multiple concurrent uploads
  - Heavy AI operations
  - Long-running sessions

**Immediate Solutions:**

**A. Upgrade to Render Paid Plans**
- **Starter Plan ($7/month):**
  - 512MB RAM (same as free, but no cold starts)
  - Best for: Light usage, faster response times
- **Standard Plan ($25/month):**
  - 2GB RAM ✅ **RECOMMENDED**
  - No cold starts
  - Handles multiple concurrent users
  - Best for: Production-ready deployment
- **Pro Plan ($85/month):**
  - 4GB RAM
  - Best for: Heavy usage, many concurrent users

**B. Alternative Hosting Providers**
- **Railway ($5/month starter):**
  - 8GB RAM on free tier during trial
  - Better resource allocation
  - No cold starts on paid plans
- **Fly.io:**
  - Pay-as-you-go pricing
  - Better memory management
  - Edge deployment for faster response
- **AWS EC2/Lambda:**
  - Flexible scaling
  - Pay only for usage
  - More configuration required
- **DigitalOcean App Platform ($12/month):**
  - 1GB RAM
  - Simple deployment
  - Good documentation

**C. Code Optimization (Short-term fixes)**
```python
# Implement streaming PDF processing
# Free up memory after each page extraction
# Use generators instead of loading all data
# Add memory monitoring and cleanup
```

**D. External Storage Migration**
- Move PDF storage to S3/R2 (offload from server memory)
- Store extracted text in MongoDB (reduce re-processing)
- Implement lazy loading for large documents

**Implementation Priority:**
1. 🔴 **Upgrade to Render Standard Plan ($25/month) - CRITICAL**
2. ✅ Migrate PDF storage to Cloudflare R2/AWS S3
3. ✅ Implement streaming PDF processing
4. ✅ Add memory monitoring and alerts
5. Consider Railway/Fly.io as alternatives

**Cost-Benefit Analysis:**
- **Free tier:** $0/month - Frequent crashes, poor UX
- **Standard tier:** $25/month - Stable, handles 10+ concurrent users
- **ROI:** Better user experience = More users = Justifies cost

### 3. PDF Type Support Expansion

**Current Limitation:**
- ⚠️ **Free tier can only reliably handle the provided sample PDFs**
- Memory constraints (512MB) prevent processing of:
  - Large PDFs (>20MB)
  - Scanned/image-heavy PDFs
  - Multiple large PDFs simultaneously
  - PDFs with complex formatting

**Why This Limitation Exists:**
- PDF extraction loads entire PDF into memory
- Text extraction is memory-intensive
- No background processing or streaming
- Limited server resources on free tier

**Future Support (After Hosting Upgrade):**

**A. Support for Various PDF Types:**
- **Text-based PDFs:** ✅ Currently supported with multi-method extraction
- **Scanned PDFs with OCR:**
  - Implement Tesseract OCR integration
  - Extract text from images in PDFs
  - Support for scanned textbooks/notes
- **Image-heavy PDFs:**
  - Optimize image handling
  - Extract text separately from images
  - Reduce memory footprint
- **Large PDFs (50MB+):**
  - Streaming processing
  - Page-by-page extraction
  - Progress tracking
- **Protected PDFs:**
  - Password-protected PDF support
  - User provides password during upload
- **Multi-column layouts:**
  - Improve text extraction accuracy
  - Preserve reading order
- **Mathematical notation:**
  - LaTeX/MathML extraction
  - Preserve equations in quizzes

**B. File Format Expansion:**
- **DOCX/DOC:** Word documents support
- **EPUB:** E-book format support
- **HTML/Markdown:** Web-based content
- **PowerPoint:** Presentation slides
- **Images (JPG/PNG):** Direct image upload with OCR

**C. Bulk Upload & Management:**
- Upload multiple PDFs at once
- Folder/category organization
- Drag-and-drop multiple files
- ZIP file upload and extraction
- Batch processing queue

**Implementation Requirements:**
1. 🔴 **PREREQUISITE: Upgrade hosting to 2GB+ RAM**
2. Implement OCR (Tesseract/Google Vision API)
3. Add streaming file processing
4. Migrate to cloud storage (S3/R2)
5. Implement background job queue (Celery)
6. Add file format converters
7. Optimize memory usage patterns

**Why Not Now:**
- Current 512MB RAM cannot handle diverse PDFs
- Would cause frequent crashes and poor UX
- Need stable infrastructure first
- Storage costs for cloud migration

**Post-Upgrade Capabilities:**
- Process PDFs up to 100MB
- Handle 5+ concurrent uploads
- Support scanned documents with OCR
- Enable batch processing
- Store unlimited PDFs in cloud storage

### 4. Enhanced LLM Integration

**Better Prompt Engineering:**
- Implement few-shot learning with example Q&A pairs
- Use chain-of-thought prompting for complex questions
- Add temperature controls for different question types
- Implement retry logic with refined prompts on failures

**Advanced Model Support:**
- Upgrade to GPT-4 or Claude 3 for better reasoning
- Support for multiple LLM providers (fallback chain)
- Fine-tuned models specifically for educational content
- Local LLM support (Ollama, LMStudio) for offline usage

### 5. YouTube Integration Enhancement

**Current Limitation:**
- Basic models often generate generic recommendations without actual YouTube links
- Recommendations may not always be real or accessible videos due to basic LLM Model

**Proposed Solution:**
- **YouTube Data API Integration:** Use official YouTube API to search and fetch real videos
- **Video Metadata:** Include thumbnails, view counts, duration, upload date
- **Direct Links:** Provide clickable links to actual YouTube videos
- **Playlist Generation:** Create custom playlists based on topics
- **Video Embedding:** Embed videos directly in the app

### 6. Delete Functionality

**PDF Deletion:**
- Add delete button for each PDF in library
- Cascade delete associated quizzes and chat history
- Confirmation dialog before deletion
- Soft delete option (archive instead of permanent delete)

**Chat History Deletion:**
- Delete individual chats
- Clear all chat history option
- Export chat before deletion

**Quiz History Deletion:**
- Delete specific quiz attempts
- Clear all progress option with warning
- Export quiz results before deletion

### 7. Multi-User Support
- User registration and authentication
- Personal dashboards and data isolation
- Share quizzes and study materials
- Leaderboards and social features

### 8. Advanced RAG
- Vector embeddings with Pinecone/Weaviate
- Semantic search for better relevance
- Multi-document query support
- Hybrid search (keyword + semantic)

### 9. Offline Support
- Progressive Web App (PWA) capabilities
- Local PDF caching
- Offline quiz generation with cached models
- Sync when back online

### 10. Accessibility
- Screen reader support
- Keyboard navigation
- High contrast mode
- Text-to-speech for questions

### 11. Analytics & Insights
- Learning patterns analysis
- Time spent per topic
- Difficulty progression tracking
- Personalized study recommendations

### 12. Export & Import
- Export progress as PDF/CSV
- Import quizzes from other formats
- Backup and restore functionality
- Share quiz templates

### 13. Mobile App
- React Native version
- Native PDF rendering
- Push notifications for study reminders
- Offline-first architecture

### 14. Collaboration Features
- Study groups
- Shared quiz sessions
- Peer-to-peer chat
- Teacher dashboard for monitoring

### 15. Gamification
- Points and badges system
- Daily streaks
- Challenge friends
- Unlock achievements

## 🤖 LLM Usage

Throughout this project, I extensively used AI coding assistants to accelerate development:

### 1. Claude/ChatGPT for Code Generation
- Generated boilerplate React components
- Created FastAPI route structures
- Wrote Tailwind CSS utility classes
- Debugged complex async/await issues

### 2. LLM for Problem Solving
- Researched best practices for RAG implementation
- Debugged MongoDB aggregation pipelines
- Optimized React render performance
- Resolved CORS and deployment issues

### 3. Documentation
- Wrote comprehensive README sections
- Created setup instructions
- Formatted code comments

### Productivity Gains
- Estimated 60-70% faster development
- Fewer syntax errors
- Better code organization
- More comprehensive error handling

### Human Input Required
- Architecture decisions
- UI/UX design choices
- Feature prioritization
- Bug fixes and edge cases
- Testing and validation

## 🧪 Testing

### Manual Testing Checklist
- ✅ PDF upload and preview
- ✅ Multi-method PDF text extraction
- ✅ Image-based PDF detection
- ✅ Quiz generation and scoring
- ✅ Chat with citations
- ✅ Progress tracking
- ✅ YouTube recommendations
- ✅ Mobile responsiveness
- ✅ Error handling

### Browser Testing
- ✅ Chrome/Edge (Primary)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers

## 🐛 Debugging Tips

### Backend Issues

**Problem: Database not connected**
```bash
# Check MongoDB URI format
# Ensure IP whitelist includes your IP
# Verify database user credentials
```

**Problem: LLM API Error**
```bash
# Check OpenRouter API key
# Verify credits balance
# Check rate limits
```

**Problem: Uvicorn not found**
```bash
# Make sure virtual environment is activated
# Reinstall dependencies: pip install -r requirements.txt
```

**Problem: Backend not responding (Render cold start)**
```bash
# Wait 30-50 seconds for cold start
# Visit /health endpoint to wake it up
# Check Render logs for errors
```

**Problem: Out of Memory Error (512MB limit)**
```bash
# CRITICAL: This is a hosting limitation
# Temporary fixes:
#   - Use smaller PDFs (<10MB)
#   - Avoid concurrent uploads
#   - Restart the service if crashed
# Permanent fix:
#   - Upgrade to Render Standard plan ($25/month, 2GB RAM)
#   - Or migrate to Railway/Fly.io
# Check Render logs for memory usage:
#   - Look for "out of memory" errors
#   - Monitor memory spikes during PDF processing
```

**Problem: PDF Text Extraction Failed**
```bash
# Check if PDF is text-based (not scanned image)
# Verify PDF is not corrupted
# Check PDF is not password-protected
# Try different PDF - the app now tries 3 extraction methods
# Check backend logs for specific error
```

### Frontend Issues

**Problem: Network Error**
```bash
# Verify backend is running
# Check VITE_API_URL in .env
# Check browser console for CORS errors
# Ensure backend is awake (not in cold start)
```

**Problem: PDF not loading**
```bash
# Check file size (<50MB)
# Verify PDF is text-based (not scanned)
# Check browser console for errors
# Wait patiently (1-2 minutes for first upload)
# If using free tier, use only sample PDFs provided
```

**Problem: Upload timeout**
```bash
# Check internet connection
# Verify backend is not in cold start
# Try smaller PDF first
# Check Render logs for backend errors
# Check for out of memory errors on free tier
```

## 📝 Git Commit Guidelines

This project follows a structured commit message convention for better code organization and history tracking.

### Initial Setup Commits

When setting up the project for the first time, the following commit sequence was used:

```bash
# Initialize repository
git init

# Create .gitignore
echo node_modules/ > .gitignore
echo uploads/ >> .gitignore
echo .env >> .gitignore
echo *.pyc >> .gitignore
echo __pycache__/ >> .gitignore
echo dist/ >> .gitignore
echo .vscode/ >> .gitignore

# Add .gitignore first
git add .gitignore
git commit -m "chore: add gitignore"

# Add dependency files
git add backend/requirements.txt frontend/package.json frontend/package-lock.json
git commit -m "chore: setup project dependencies"

# Commit backend
git add backend/
git commit -m "feat: implement FastAPI backend with MongoDB and AI integration"

# Commit frontend
git add frontend/
git commit -m "feat: build responsive React frontend with Tailwind CSS"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/smartstudy.git
git branch -M main
git push -u origin main
```

**Note:** The codebase has been updated according to deployment requirements. Please check the latest commits for deployment-related configurations and improvements.


## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes following the commit guidelines above
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Pull Request Guidelines

- Follow the existing code style
- Update documentation as needed
- Add tests for new features
- Ensure all tests pass
- Keep PRs focused on a single feature/fix
- Write clear PR descriptions

## 📝 License

This project is MIT licensed.

## 👨‍💻 Author

**Abhijeet Suryavanshi**
- Email: abhijeets20032000@gmail.com

## 🙏 Acknowledgments

- NCERT for Class XI Physics PDFs
- OpenRouter for LLM API access
- MongoDB Atlas for database hosting
- Vercel and Render for free hosting
- The React and FastAPI communities

---

**Built with ❤️ using React, FastAPI, and AI**

*Last Updated: October 9, 2025*
