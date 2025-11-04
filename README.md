# SmartStudy - AI-Powered Learning Assistant 🎓

An intelligent learning platform that transforms your educational PDFs into interactive study experiences using AI. Upload NCERT textbooks or any educational material and get instant quizzes, AI tutoring, progress tracking, and personalized video recommendations.

![SmartStudy Banner](https://img.shields.io/badge/AI-Powered-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green) ![React](https://img.shields.io/badge/React-Frontend-blue) ![MongoDB](https://img.shields.io/badge/MongoDB-Database-green)

## ✨ Features

### 📚 Smart PDF Management
- **Multi-format Support**: Upload and process PDF textbooks with advanced text extraction
- **Fallback Processing**: Intelligent text extraction using pdfplumber, PyMuPDF, and PyPDF2
- **Image-based PDF Detection**: Automatically identifies scanned PDFs
- **Real-time Preview**: View your PDFs directly in the browser
- **Delete Management**: Remove PDFs with confirmation dialogs

### 🎯 AI Quiz Generation
- **Customizable Quizzes**: Generate MCQ, Short Answer, and Long Answer questions
- **Smart Question Distribution**: Choose the number of each question type
- **Instant Feedback**: Get detailed explanations for every answer
- **Score Analytics**: Track your performance with visual charts
- **Retry Options**: Generate new quizzes anytime

### 💬 AI Teacher Chat
- **Context-Aware Responses**: Ask questions about your uploaded PDFs
- **Citation System**: Get answers with page references
- **Chat History**: Review past conversations
- **Multi-Session Support**: Manage multiple chat threads
- **Delete Conversations**: Remove chat history when needed

### 📊 Progress Dashboard
- **Performance Metrics**: Overall score, total quizzes, questions answered
- **Trend Analysis**: Line charts showing score progression
- **Strengths & Weaknesses**: AI-identified focus areas
- **Recent Activity**: Quick view of latest quiz attempts

### 🎥 YouTube Recommendations
- **Topic-Based Search**: Get curated video recommendations for any subject
- **AI-Powered Selection**: Smart filtering of educational content
- **Channel Information**: Know the source of each recommendation
- **Quick Topics**: One-click suggestions for popular subjects

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: Document database with Motor async driver
- **OpenRouter API**: GPT-3.5-turbo for AI responses
- **PDF Processing**: pdfplumber, PyMuPDF (fitz), PyPDF2
- **Python 3.8+**: Modern Python features

### Frontend
- **React 18**: Modern UI library with hooks
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first styling
- **React Router**: Client-side routing
- **Recharts**: Beautiful data visualization
- **Lucide Icons**: Modern icon system
- **Axios**: HTTP client

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm/yarn
- **MongoDB** (local or Atlas)
- **OpenRouter API Key** (for AI features)

## 🚀 Installation & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd smartstudy
```

### 2. Backend Setup
```bash
# Navigate to backend directory (if separate) or project root
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn motor pymongo python-multipart
pip install pdfplumber PyPDF2 PyMuPDF
pip install httpx python-dotenv

# Or install from requirements.txt if available
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the backend directory:
```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
# Or for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority

# Database Name
DATABASE_NAME=beyondchats_db

# OpenRouter API Key (Get from https://openrouter.ai/)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Change model
# MODEL_NAME=openai/gpt-3.5-turbo
```

### 4. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data
```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Add your IP to Network Access whitelist
4. Create database user
5. Get connection string and update `MONGODB_URI`

### 5. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend  # or cd src if structure is different

# Install dependencies
npm install

# Or using yarn
yarn install
```

Create `.env` file in frontend directory (optional):
```env
VITE_API_URL=http://localhost:8000
```

## 🎮 Running the Application

### Start Backend Server
```bash
# From backend directory
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run on: `http://localhost:8000`

### Start Frontend Development Server
```bash
# From frontend directory
npm run dev

# Or using yarn
yarn dev
```

Frontend will run on: `http://localhost:3000`

## 📁 Project Structure
```
smartstudy/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   └── uploads/                # PDF storage directory
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main app component & routing
│   │   ├── components.jsx     # All page components
│   │   ├── api.js             # API client functions
│   │   ├── utils.js           # Utility functions
│   │   ├── styles.css         # Global styles & animations
│   │   └── main.jsx           # React entry point
│   │
│   ├── index.html             # HTML template
│   ├── package.json           # Node dependencies
│   ├── vite.config.js         # Vite configuration
│   ├── tailwind.config.js     # Tailwind CSS config
│   └── postcss.config.js      # PostCSS config
│
└── README.md
```

## 🔌 API Endpoints

### PDF Management
- `POST /api/pdf/upload` - Upload PDF file
- `GET /api/pdf/list` - List all PDFs
- `GET /api/pdf/{pdf_id}` - Download PDF file
- `GET /api/pdf/{pdf_id}/text` - Get extracted text
- `DELETE /api/pdf/{pdf_id}` - Delete PDF

### Quiz Operations
- `POST /api/quiz/generate` - Generate quiz questions
- `POST /api/quiz/submit` - Submit quiz answers

### Chat Operations
- `POST /api/chat` - Send message to AI teacher
- `GET /api/chat/history` - Get chat history
- `GET /api/chat/{chat_id}` - Get specific chat
- `DELETE /api/chat/{chat_id}` - Delete chat

### Progress & Analytics
- `GET /api/progress` - Get user progress stats

### Recommendations
- `POST /api/recommend/youtube` - Get video recommendations

## 🎨 UI Features

### Modern Design Elements
- **Glassmorphism**: Frosted glass effects
- **Gradient Backgrounds**: Smooth color transitions
- **Card Hover Effects**: Interactive 3D transforms
- **Loading States**: Elegant spinners and skeletons
- **Responsive Design**: Mobile-first approach
- **Dark/Light Accents**: Beautiful color schemes

### Animations
- **Fade In**: Smooth page transitions
- **Scale Hover**: Card interactions
- **Pulse Effects**: Loading indicators
- **Slide Animations**: Modal appearances

## 🔧 Configuration

### Customizing AI Model

Edit in `main.py`:
```python
MODEL_NAME = "openai/gpt-3.5-turbo"  # Change to any OpenRouter model
```

Available models:
- `openai/gpt-3.5-turbo` (Fast, cost-effective)
- `openai/gpt-4` (More accurate, slower)
- `anthropic/claude-2` (Alternative)

### Adjusting Upload Limits
```python
# In main.py upload endpoint
max_file_size = 50 * 1024 * 1024  # 50MB default
```

### Customizing Quiz Generation
```python
# Default question counts in frontend
numMcq = 5   # Multiple choice
numSaq = 3   # Short answer
numLaq = 2   # Long answer
```

## 🐛 Troubleshooting

### Backend Issues

**MongoDB Connection Error**
```bash
# Check if MongoDB is running
mongod --version

# Verify connection string in .env
# For Atlas: Check IP whitelist and credentials
```

**PDF Upload Fails**
```bash
# Check uploads directory exists
mkdir uploads

# Verify file permissions
chmod 755 uploads
```

**OpenRouter API Error**
```bash
# Verify API key is valid
# Check balance at https://openrouter.ai/
# Ensure MODEL_NAME is correct
```

### Frontend Issues

**API Connection Error**
```bash
# Verify backend is running on port 8000
# Check VITE_API_URL in .env
# Check browser console for CORS errors
```

**Build Errors**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

## 📈 Performance Tips

### Backend Optimization
- Use MongoDB indexes for faster queries
- Enable MongoDB connection pooling
- Cache frequently accessed PDFs
- Implement rate limiting for API endpoints

### Frontend Optimization
- Lazy load routes with React.lazy()
- Implement virtual scrolling for large lists
- Use React.memo for expensive components
- Optimize images and assets

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` files
- **File Upload**: Validate file types and sizes
- **MongoDB**: Use authentication in production
- **CORS**: Configure proper origins
- **Rate Limiting**: Implement for public APIs

## 🚀 Deployment

### Backend (FastAPI)

**Option 1: Railway/Render**
```bash
# Add Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Option 2: Docker**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (React)

**Option 1: Vercel**
```bash
npm run build
vercel deploy
```

**Option 2: Netlify**
```bash
npm run build
netlify deploy --prod --dir=dist
```

## 📝 License

MIT License - feel free to use this project for learning and development.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## 🎓 Educational Use

This project is designed for educational purposes. Perfect for:
- Learning full-stack development
- Understanding AI integration
- Building portfolio projects
- Teaching web development concepts

---

**Built with ❤️ using React, FastAPI, and AI**

*Transform your learning experience with SmartStudy!*
