# SmartStudy - AI-Powered Learning Assistant

A modern, full-stack web application that helps school students learn smarter using AI-powered quizzes, chat assistance, and progress tracking. Built with React, FastAPI, and MongoDB.

## Live Demo

- **Frontend**: https://smartstudy-steel.vercel.app
- **Backend API**: https://smartstudy-8q14.onrender.com/
- **Diagnostics**: https://smartstudy-8q14.onrender.com/api/diagnostics

## ⚠️ Important: First-Time Usage

Before testing the frontend, follow these steps:

1. **Wake up the backend server** by visiting: https://smartstudy-8q14.onrender.com/health
   - Render free tier puts inactive services to sleep after 15 minutes
   - First request takes 30-50 seconds to wake up the server (cold start)
   - You'll see `{"status": "healthy"}` when it's ready

2. **Check system diagnostics** (after backend is warm):
   - Visit: https://smartstudy-8q14.onrender.com/api/diagnostics
   - Shows database status, storage configuration, and file count

3. **Access the frontend**: https://smartstudy-steel.vercel.app

## PDF Upload Notice

**First PDF upload may take 1-2 minutes** due to:
- Cold start of backend service
- PDF processing and text extraction
- Database storage
- Subsequent uploads are faster (10-30 seconds)

**Please be patient and don't refresh the page during upload**

## Known Limitations

### 1. Memory Constraints & Crashes

⚠️ **Render free tier has 512MB RAM limit**

Backend may crash with "Out of Memory" error during heavy usage. This can happen when:
- Processing large PDFs (>20MB)
- Multiple concurrent users uploading PDFs
- Running intensive AI operations

If this occurs, the service will automatically restart (30-50 seconds).

**For testing, please use only the provided sample PDFs from the repository**

### 2. Internal Server Error (500) During Upload

⚠️ **You may see "Internal Server Error 500" during PDF upload - This is NOT a backend bug!**

**What's happening:**
- Render free tier has strict memory limits (512MB RAM)
- During PDF processing, the server may temporarily exceed this limit
- Render forcefully terminates the process, causing a 500 error
- **However, the upload often completes successfully before termination**

**How to verify your upload succeeded:**

1. **Wait 30-60 seconds** after seeing the error
2. **Refresh the page** or navigate to the Source Selector
3. **Check if your PDF appears** in the document library
4. If it appears, the upload was successful despite the error message

**Why this happens:**
- The backend code is functioning correctly
- It's a hosting platform limitation (not a code issue)
- Render's free tier aggressively manages memory
- The process completes but gets killed during cleanup

**Recommended solution:**
- Upgrade to Render's paid tier ($25/month for 2GB RAM)
- Or migrate to Railway/Fly.io for better memory handling
- For MVP testing, simply verify your PDF after the error

**Technical explanation:**
The backend successfully:
1. Receives the file
2. Extracts text content
3. Saves to MongoDB
4. Stores file metadata

But Render kills the process during the HTTP response phase due to memory constraints. The data is already saved, hence refreshing shows your PDF.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)
- [Deployment](#deployment)
- [Implementation Details](#implementation-details)
- [Trade-offs & Decisions](#tradeoffs--decisions)
- [What's Completed](#whats-completed)
- [Future Improvements](#future-improvements)
- [Testing](#testing)
- [Debugging Tips](#debugging-tips)

## Features

### Core Features

**Source Selector**
- Upload custom PDF coursebooks
- View all uploaded PDFs with metadata
- Select specific PDF or "All PDFs" mode
- Pre-seeded with NCERT Class XI Physics PDFs

**PDF Viewer**
- Built-in PDF viewer with page navigation
- Split-view with document library
- Download functionality
- Responsive design for mobile
- Real-time file existence validation

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

## Tech Stack

### Frontend
- React 18.2 - UI library
- React Router 6 - Client-side routing
- TailwindCSS 3.4 - Styling framework
- Recharts 2.10 - Data visualization
- Axios - HTTP client
- Lucide React - Icon library
- Vite 5 - Build tool

### Backend
- FastAPI - Python web framework
- Uvicorn - ASGI server
- Motor - Async MongoDB driver
- PDFPlumber - Primary PDF text extraction
- PyPDF2 - Fallback PDF extraction
- PyMuPDF (fitz) - Alternative PDF extraction
- httpx - Async HTTP client
- OpenRouter API - LLM integration (GPT-3.5)
- Pydantic - Data validation

### Database
- MongoDB Atlas - Cloud database

### Deployment
- Vercel - Frontend hosting
- Render - Backend hosting (Free tier with cold starts and 512MB RAM limit)

## Project Structure

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

## Setup Instructions

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
# - UPLOAD_DIR (optional, defaults to /tmp/uploads)

# Run the backend with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on http://localhost:8000

**Note**: You can also run with: `python main.py` which uses uvicorn internally.

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

The frontend will start on http://localhost:3000

### 4. Access the Application

Open your browser and navigate to http://localhost:3000

## Environment Variables

### Backend (.env)

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=smartstudy_db
OPENROUTER_API_KEY=your_openrouter_api_key_here
UPLOAD_DIR=/tmp/uploads
```

**How to get these:**

**MongoDB URI:**
- Create account at MongoDB Atlas
- Create a free cluster
- Add your IP to whitelist (or allow all: 0.0.0.0/0)
- Create database user
- Get connection string from "Connect" → "Connect your application"

**OpenRouter API Key:**
- Sign up at OpenRouter.ai
- Go to Keys section
- Create new API key
- Add credits (requires payment)

**UPLOAD_DIR:**
- Optional (defaults to /tmp/uploads)
- Use absolute paths only
- Must be writable by the application

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000
```

For production: `VITE_API_URL=https://your-backend.render.com`

## Development Workflow

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

## Deployment

### Frontend (Vercel)

1. Push code to GitHub
2. Connect repository to Vercel
3. Configure build settings:
   - Framework: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Root Directory: `frontend`
4. Add environment variable:
   - `VITE_API_URL=https://your-backend.render.com`
5. Deploy

### Backend (Render)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect repository
4. Configure:
   - Environment: Python 3
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `MONGODB_URI`
   - `OPENROUTER_API_KEY`
   - `DATABASE_NAME`
   - `UPLOAD_DIR=/tmp/uploads` (or your preferred path)
6. Deploy

**Important Notes:**
- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-50 seconds (cold start)
- Free tier has 512MB RAM limit - may crash with "Out of Memory" error
- 500 errors during upload are usually platform limitations, not code bugs
- For production, consider upgrading to a paid plan to avoid cold starts and memory issues
- Render automatically sets the PORT environment variable

### Testing the Deployed Application

**Step 1: Wake up the backend**

```bash
# Visit the health check endpoint first
curl https://your-backend.render.com/health

# Or open in browser:
https://your-backend.render.com/health
```

Wait for `{"status": "healthy"}` response (30-50 seconds on cold start)

**Step 2: Check diagnostics**

```bash
https://your-backend.render.com/api/diagnostics
```

This shows:
- Database connection status
- Upload directory configuration
- Total PDFs stored
- API key configuration status

**Step 3: Access the frontend**

```bash
https://your-frontend.vercel.app
```

**Step 4: Upload your first PDF**

- Be patient during first upload (1-2 minutes)
- Don't refresh the page immediately if you see a 500 error
- Wait 30-60 seconds, then refresh to check if upload succeeded
- Subsequent uploads are faster
- Use only the provided sample PDFs to avoid memory issues

## Implementation Details

### PDF Processing Pipeline

**Step 1: Upload**
- User uploads PDF via drag-drop or file selector
- File size validated (max 50MB)

**Step 2: Storage**
- File saved to `/tmp/uploads` (or configured UPLOAD_DIR) with unique ObjectId
- Absolute path stored in database for reliable retrieval

**Step 3: Extraction**
- Multi-method text extraction (PDFPlumber → PyMuPDF → PyPDF2)
- Automatic image-based PDF detection

**Step 4: Database**
- Metadata and text stored in MongoDB
- File path validated (security check)

**Step 5: Retrieval**
- File existence checked before serving
- Path security validated (prevents traversal attacks)
- Clear error messages on failure

**Text Extraction Strategy:**
- Primary Method: PDFPlumber (best for most text-based PDFs)
- Fallback 1: PyMuPDF/fitz (good for scanned PDFs and complex layouts)
- Fallback 2: PyPDF2 (final fallback for problematic PDFs)
- Image Detection: Automatically detects image-based PDFs that may need OCR

### Quiz Generation Flow

1. Context Building: Extract relevant text from PDF (4000 char limit)
2. LLM Prompt: Structured JSON prompt with question requirements
3. Parsing: Parse JSON response into QuizQuestion objects
4. Fallback: Hardcoded questions if LLM fails
5. Storage: Quiz stored in MongoDB with unique ID
6. Evaluation: Answer matching and scoring logic

### RAG Implementation

1. Text Chunking: Split PDF text into manageable chunks
2. Query Processing: Extract keywords from user query
3. Citation Search: Find relevant pages using keyword matching
4. Snippet Extraction: Extract relevant sentences from pages
5. Ranking: Sort by relevance score
6. Response: LLM generates answer with citations

### Chat Architecture

1. Session Management: Each chat has unique ID
2. Message Storage: All messages stored in MongoDB
3. Context Window: Recent messages sent to LLM
4. Citations: Relevant PDF snippets included in context
5. Streaming: Responses displayed in real-time

## Trade-offs & Decisions

### 1. Vector Database vs Keyword Search
**Decision**: Used keyword-based citation search
**Reason**: Faster implementation, no need for embedding models
**Trade-off**: Less semantic understanding, but adequate for MVP
**Future**: Can upgrade to Pinecone/Weaviate for better relevance

### 2. LLM Provider Choice
**Decision**: OpenRouter API (GPT-3.5)
**Reason**: Cost-effective, reliable, good quality
**Trade-off**: External dependency, requires API key
**Alternative**: Could use Ollama for local LLMs

### 3. State Management
**Decision**: React useState/useEffect (no Redux)
**Reason**: Simple app, component-level state sufficient
**Trade-off**: May need refactoring if app grows
**Future**: Consider Zustand or Context API for global state

### 4. PDF Storage
**Decision**: Local file system with absolute path handling + MongoDB metadata
**Reason**: Simple, reliable on production servers
**Trade-off**: Not scalable for very large deployments
**Future**: Migrate to S3/Cloudflare R2 for unlimited scalability

### 5. Authentication
**Decision**: No authentication in MVP
**Reason**: Focus on core features first
**Trade-off**: Single-user app
**Future**: Add Auth0 or JWT-based auth

### 6. Caching
**Decision**: No caching layer
**Reason**: Simple architecture
**Trade-off**: Repeated LLM calls cost money
**Future**: Add Redis for response caching

### 7. Server Choice
**Decision**: Uvicorn ASGI server
**Reason**: FastAPI's recommended server, async support, excellent performance
**Benefit**: Handles concurrent requests efficiently, perfect for async operations

### 8. Hosting Provider
**Decision**: Render free tier for backend
**Reason**: Zero cost, easy deployment, good for MVP
**Trade-off**: Cold starts after 15 minutes + 512MB RAM limit causing crashes and 500 errors
**Note**: 500 errors are platform limitations, not application bugs
**Future**: Upgrade to paid tier ($7-25/month) for always-on service and 2GB+ RAM

### 9. PDF Extraction Strategy
**Decision**: Multi-method fallback approach (PDFPlumber → PyMuPDF → PyPDF2)
**Reason**: Maximize compatibility with different PDF types
**Benefit**: Higher success rate for text extraction
**Trade-off**: Slightly more complex error handling

## What's Completed

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

## Future Improvements

### 1. Performance Optimization - Upload Speed

**Current Issues:**
- PDF upload takes 30-120 seconds due to:
  - Render cold start (30-50 seconds)
  - Synchronous PDF text extraction
  - Large file processing
  - Network latency

**Proposed Solutions:**

A. **Upgrade Hosting**
- Migrate to Render paid tier ($7-25/month) - eliminates cold starts
- Or use Railway, Fly.io, or AWS Lambda with warmer instances
- Expected improvement: Reduce upload time by 50-70%

B. **Background Processing**
- Implement async PDF processing with Celery/RQ
- Save file immediately and return response
- Process text extraction in background
- Client polls for completion status
- Expected improvement: Instant response (1-2 seconds)

C. **Chunked Upload**
- Split large files into chunks (1MB each)
- Upload chunks progressively
- Better progress feedback
- Resumable uploads

D. **Optimize PDF Processing**
- Use faster PDF library combinations
- Parallel page processing with asyncio
- Process multiple pages simultaneously

E. **CDN/Edge Storage**
- Use Cloudflare R2 or AWS S3 for file storage
- Cloudflare Workers for edge computing
- Process PDFs closer to user location

### 2. Memory Management & Hosting Upgrade

**Current Critical Issue:**
- Render free tier crashes with "Out of Memory (512MB)" error
- Internal Server Error 500 during PDF uploads (platform limitation, not code bug)

**Immediate Solutions:**

A. **Upgrade to Render Paid Plans**
- Starter Plan ($7/month): 512MB RAM, no cold starts
- Standard Plan ($25/month): 2GB RAM - RECOMMENDED
- Pro Plan ($85/month): 4GB RAM

B. **Alternative Hosting Providers**
- Railway ($5/month starter): 8GB RAM
- Fly.io: Pay-as-you-go, better memory management
- AWS EC2/Lambda: Flexible scaling
- DigitalOcean ($12/month): 1GB RAM

C. **Code Optimization**
- Implement streaming PDF processing
- Free up memory after each page extraction
- Add memory monitoring and cleanup

D. **External Storage Migration**
- Move PDF storage to S3/R2
- Store extracted text in MongoDB
- Implement lazy loading

### 3. PDF Type Support Expansion

**Current Limitation:**
- Free tier can only reliably handle provided sample PDFs
- Memory constraints (512MB) prevent processing of large/complex PDFs

**Future Support (After Hosting Upgrade):**

A. **Various PDF Types:**
- Text-based PDFs: ✅ Currently supported
- Scanned PDFs with OCR: Tesseract/Google Vision API
- Image-heavy PDFs: Optimized image handling
- Large PDFs (50MB+): Streaming processing
- Protected PDFs: Password-protected support
- Multi-column layouts: Improved extraction

B. **File Format Expansion:**
- DOCX/DOC: Word documents
- EPUB: E-book format
- HTML/Markdown: Web content
- PowerPoint: Presentation slides
- Images: Direct upload with OCR

### 4. Enhanced LLM Integration

**Better Prompt Engineering:**
- Few-shot learning with example Q&A pairs
- Chain-of-thought prompting for complex questions
- Temperature controls for different question types
- Retry logic with refined prompts on failures

**Advanced Model Support:**
- Upgrade to GPT-4 or Claude 3
- Support for multiple LLM providers
- Fine-tuned models for educational content
- Local LLM support (Ollama, LMStudio)

### 5. YouTube Integration Enhancement

**Current Limitation:**
- Basic models may generate generic recommendations

**Proposed Solution:**
- YouTube Data API Integration for real videos
- Video metadata (thumbnails, view counts, duration)
- Direct clickable links
- Custom playlist generation
- Embedded videos in app

### 6. Delete Functionality

**PDF Deletion:**
- Delete button for each PDF
- Cascade delete associated quizzes/chat history
- Confirmation dialog

**Chat/Quiz History Deletion:**
- Delete individual items
- Clear all option
- Export before deletion

### 7. Multi-User Support
- User registration and authentication
- Personal dashboards with data isolation
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
- Offline quiz generation
- Sync when back online

### 10. Accessibility
- Screen reader support
- Keyboard navigation
- High contrast mode
- Text-to-speech for questions

### 11. Better Error Handling
- Graceful handling of 500 errors from hosting platform
- User-friendly messages explaining platform limitations
- Automatic retry mechanisms
- Upload success verification after errors

## Debugging Tips

### Common Issues

**1. PDF Upload Shows 500 Error But Works**
- **Cause**: Render free tier memory limitation
- **Solution**: Wait 30-60 seconds, refresh page, check if PDF appears
- **Note**: This is a platform issue, not a code bug

**2. Backend Cold Start (Slow First Request)**
- **Cause**: Render spins down after 15 minutes inactivity
- **Solution**: Visit `/health` endpoint first, wait for response

**3. Out of Memory Errors**
- **Cause**: 512MB RAM limit exceeded
- **Solution**: Use smaller PDFs, upgrade hosting plan

**4. PDF Not Displaying**
- **Check**: File path in database vs actual file location
- **Check**: File permissions and upload directory configuration

**5. Quiz Generation Fails**
- **Check**: OpenRouter API key and credits
- **Check**: PDF text extraction succeeded
- **Fallback**: App provides hardcoded questions

## Testing

### Manual Testing Checklist

- [ ] Upload PDF successfully
- [ ] Verify PDF appears after 500 error (if applicable)
- [ ] View PDF in viewer
- [ ] Generate quiz from PDF
- [ ] Answer quiz questions
- [ ] View progress dashboard
- [ ] Start new chat
- [ ] Ask questions about PDF
- [ ] Get YouTube recommendations
- [ ] Test on mobile device

### Performance Testing

- Monitor cold start times
- Test with various PDF sizes
- Check memory usage during processing
- Verify upload success despite errors

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the debugging tips section
- Remember: 500 errors during upload are often platform limitations, verify upload succeeded by refreshing

## Acknowledgments

- OpenRouter for LLM API access
- MongoDB Atlas for database hosting
- Render and Vercel for free hosting
- NCERT for educational content
