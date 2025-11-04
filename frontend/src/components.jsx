import React, { useState, useEffect, useRef } from 'react';
import { Upload, FileText, Send, Plus, Check, X, RefreshCw, Download, MessageCircle, BarChart3, Youtube, TrendingUp, Award, Target, Sparkles, BookOpen, Zap, Trash2, AlertCircle } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import * as api from './api';
import { formatDate, formatScore, truncateText, getScoreColor, getScoreBgColor } from './utils';

// ============================================================================
// HOME PAGE
// ============================================================================
export function HomePage() {
  const [pdfs, setPdfs] = useState([]);
  const [selectedPdf, setSelectedPdf] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [pdfToDelete, setPdfToDelete] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    loadPDFs();
  }, []);

  const loadPDFs = async () => {
    try {
      const data = await api.listPDFs();
      setPdfs(data.pdfs);
      
      // Update selected PDF if it was deleted
      if (selectedPdf && !data.pdfs.find(p => p.pdf_id === selectedPdf.pdf_id)) {
        setSelectedPdf(data.pdfs.length > 0 ? data.pdfs[0] : null);
      } else if (data.pdfs.length > 0 && !selectedPdf) {
        setSelectedPdf(data.pdfs[0]);
      }
    } catch (error) {
      console.error('Failed to load PDFs:', error);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      await api.uploadPDF(file);
      await loadPDFs();
      alert('PDF uploaded successfully!');
    } catch (error) {
      alert('Failed to upload PDF: ' + error.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteClick = (pdf, e) => {
    e.stopPropagation();
    setPdfToDelete(pdf);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!pdfToDelete) return;
    
    setDeleting(pdfToDelete.pdf_id);
    try {
      await api.deletePDF(pdfToDelete.pdf_id);
      await loadPDFs();
      setShowDeleteModal(false);
      setPdfToDelete(null);
    } catch (error) {
      alert('Failed to delete PDF: ' + error.message);
    } finally {
      setDeleting(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setPdfToDelete(null);
  };

  return (
    <div className="max-w-7xl mx-auto fade-in">
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 fade-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Delete PDF?</h2>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <span className="font-semibold">"{pdfToDelete?.filename}"</span>? 
              This action cannot be undone.
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={handleDeleteCancel}
                className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-xl font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={deleting === pdfToDelete?.pdf_id}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-500 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deleting === pdfToDelete?.pdf_id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="mb-8 relative overflow-hidden bg-gradient-to-r from-primary via-purple-600 to-secondary rounded-2xl p-8 shadow-2xl">
        <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-4xl">✨</span>
            <h1 className="text-4xl font-bold text-white">Welcome to SmartStudy</h1>
          </div>
          <p className="text-indigo-100 text-lg">Transform your learning experience with AI-powered tools that make studying smarter, faster, and more effective!</p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 card-hover border border-gray-100">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg">
            <Upload className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Upload Your Coursebook</h2>
            <p className="text-gray-500 text-sm">PDF format • NCERT or any educational material</p>
          </div>
        </div>
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            className="hidden"
            id="pdf-upload"
          />
          <label
            htmlFor="pdf-upload"
            className={`
              btn-primary cursor-pointer flex items-center gap-2
              ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <Upload className="w-5 h-5" />
            {uploading ? 'Uploading...' : 'Choose PDF File'}
          </label>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Instant AI processing • Secure upload</span>
          </div>
        </div>
      </div>

      {/* PDF List & Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* PDF List */}
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">Your Library</h2>
                <p className="text-xs text-gray-500">{pdfs.length} documents</p>
              </div>
            </div>
          </div>
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
            {pdfs.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-gray-400 text-sm">No PDFs uploaded yet</p>
                <p className="text-gray-400 text-xs mt-1">Upload your first document to begin</p>
              </div>
            ) : (
              pdfs.map((pdf) => (
                <div
                  key={pdf.pdf_id}
                  onClick={() => setSelectedPdf(pdf)}
                  className={`
                    group relative p-4 rounded-xl cursor-pointer transition-all duration-200 border-2
                    ${selectedPdf?.pdf_id === pdf.pdf_id
                      ? 'border-primary bg-gradient-to-r from-primary/10 to-secondary/10 shadow-lg scale-105'
                      : 'border-gray-200 hover:border-primary/50 hover:shadow-md'
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      selectedPdf?.pdf_id === pdf.pdf_id 
                        ? 'bg-gradient-to-br from-primary to-secondary' 
                        : 'bg-gray-100'
                    }`}>
                      <FileText className={`w-5 h-5 ${selectedPdf?.pdf_id === pdf.pdf_id ? 'text-white' : 'text-gray-600'}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm text-gray-900 truncate mb-1">
                        {pdf.filename}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>{pdf.total_pages} pages</span>
                        <span>•</span>
                        <span>{formatDate(pdf.uploaded_at).split(',')[0]}</span>
                      </div>
                    </div>
                    
                    {/* Delete Button */}
                    <button
                      onClick={(e) => handleDeleteClick(pdf, e)}
                      disabled={deleting === pdf.pdf_id}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-red-100 rounded-lg disabled:opacity-50"
                      title="Delete PDF"
                    >
                      <Trash2 className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* PDF Viewer */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900">Document Preview</h2>
            {selectedPdf && (
              <a
                href={api.getPDFFile(selectedPdf.pdf_id)}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary to-secondary text-white rounded-lg hover:shadow-lg transition-all duration-200 text-sm font-medium"
              >
                <Upload className="w-4 h-4" />
                Download
              </a>
            )}
          </div>
          {selectedPdf ? (
            <div className="border-2 border-gray-200 rounded-xl overflow-hidden shadow-inner">
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-3 flex items-center justify-between border-b">
                <span className="text-sm font-semibold text-gray-700">{selectedPdf.filename}</span>
                <span className="text-xs text-gray-500">{selectedPdf.total_pages} pages</span>
              </div>
              <iframe
                src={api.getPDFFile(selectedPdf.pdf_id)}
                className="w-full h-[600px]"
                title="PDF Viewer"
              />
            </div>
          ) : (
            <div className="border-2 border-dashed border-gray-300 rounded-xl h-[600px] flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-primary/20 to-secondary/20 rounded-full flex items-center justify-center">
                  <FileText className="w-12 h-12 text-primary" />
                </div>
                <p className="text-lg font-semibold text-gray-700 mb-2">Select a document to preview</p>
                <p className="text-sm text-gray-500">Choose from your library or upload a new PDF</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <QuickActionCard
            title="Generate Quiz"
            description="Test your knowledge with AI-generated questions from your coursebook"
            icon={FileText}
            href="/quiz"
            gradient="from-blue-500 to-cyan-500"
          />
          <QuickActionCard
            title="Ask AI Teacher"
            description="Get instant answers and detailed explanations 24/7"
            icon={MessageCircle}
            href="/chat"
            gradient="from-purple-500 to-pink-500"
          />
          <QuickActionCard
            title="Track Progress"
            description="Monitor your learning journey with detailed analytics"
            icon={BarChart3}
            href="/progress"
            gradient="from-green-500 to-emerald-500"
          />
        </div>
      </div>
    </div>
  );
}

function QuickActionCard({ title, description, icon: Icon, href, gradient }) {
  return (
    <a
      href={href}
      className="block group"
    >
      <div className="relative p-6 bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 card-hover overflow-hidden">
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
        <div className="relative z-10">
          <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
            <Icon className="w-7 h-7 text-white" />
          </div>
          <h3 className="font-bold text-lg mb-2 text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
          <div className="mt-4 flex items-center text-sm font-semibold text-primary group-hover:gap-2 gap-1 transition-all">
            <span>Get started</span>
            <span className="transform group-hover:translate-x-1 transition-transform">→</span>
          </div>
        </div>
      </div>
    </a>
  );
}

// ============================================================================
// QUIZ PAGE
// ============================================================================
export function QuizPage() {
  const [pdfs, setPdfs] = useState([]);
  const [selectedPdf, setSelectedPdf] = useState('all');
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState(null);
  const [numMcq, setNumMcq] = useState(5);
  const [numSaq, setNumSaq] = useState(3);
  const [numLaq, setNumLaq] = useState(2);

  useEffect(() => {
    loadPDFs();
  }, []);

  const loadPDFs = async () => {
    try {
      const data = await api.listPDFs();
      setPdfs(data.pdfs);
    } catch (error) {
      console.error('Failed to load PDFs:', error);
    }
  };

  const handleGenerateQuiz = async () => {
    setLoading(true);
    setResults(null);
    setAnswers({});
    try {
      const pdfId = selectedPdf === 'all' ? null : selectedPdf;
      const data = await api.generateQuiz(pdfId, numMcq, numSaq, numLaq);
      setQuiz(data);
    } catch (error) {
      alert('Failed to generate quiz: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitQuiz = async () => {
    if (!quiz) return;

    const answerArray = quiz.questions.map((_, idx) => ({
      question_index: idx,
      user_answer: answers[idx] || '',
    }));

    setLoading(true);
    try {
      const data = await api.submitQuiz(quiz.quiz_id, answerArray);
      setResults(data);
    } catch (error) {
      alert('Failed to submit quiz: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex, answer) => {
    setAnswers({ ...answers, [questionIndex]: answer });
  };

  return (
    <div className="max-w-4xl mx-auto fade-in">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Quiz Generator</h1>
            <p className="text-gray-500">AI-powered questions tailored to your coursebook</p>
          </div>
        </div>
      </div>

      {!quiz && !results && (
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary" />
            Create New Quiz
          </h2>
          
          {/* PDF Selector */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Select Source Material
            </label>
            <select
              value={selectedPdf}
              onChange={(e) => setSelectedPdf(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl input-focus font-medium"
            >
              <option value="all">All PDFs</option>
              {pdfs.map((pdf) => (
                <option key={pdf.pdf_id} value={pdf.pdf_id}>
                  {pdf.filename}
                </option>
              ))}
            </select>
          </div>

          {/* Question Count */}
          <div className="mb-8">
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Question Distribution
            </label>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">
                  Multiple Choice
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={numMcq}
                  onChange={(e) => setNumMcq(parseInt(e.target.value))}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl input-focus font-bold text-center text-lg"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">
                  Short Answer
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={numSaq}
                  onChange={(e) => setNumSaq(parseInt(e.target.value))}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl input-focus font-bold text-center text-lg"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-2">
                  Long Answer
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={numLaq}
                  onChange={(e) => setNumLaq(parseInt(e.target.value))}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl input-focus font-bold text-center text-lg"
                />
              </div>
            </div>
            <div className="mt-3 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-100">
              <p className="text-sm text-gray-700">
                <span className="font-semibold">Total Questions: {numMcq + numSaq + numLaq}</span> • 
                Estimated time: {Math.ceil((numMcq * 1.5 + numSaq * 3 + numLaq * 5) / 60)} minutes
              </p>
            </div>
          </div>

          <button
            onClick={handleGenerateQuiz}
            disabled={loading || pdfs.length === 0}
            className="w-full btn-primary flex items-center justify-center gap-3 text-lg py-4"
          >
            {loading ? (
              <>
                <div className="spinner w-6 h-6 border-2" />
                Generating Quiz...
              </>
            ) : (
              <>
                <Sparkles className="w-6 h-6" />
                Generate Quiz
              </>
            )}
          </button>
        </div>
      )}

      {/* Quiz Questions */}
      {quiz && !results && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
            <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-gray-100">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-1">
                  Your Quiz
                </h2>
                <p className="text-gray-500">{quiz.total_questions} questions • Answer all to submit</p>
              </div>
              <button
                onClick={() => setQuiz(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-gray-500" />
              </button>
            </div>

            <div className="space-y-6">
              {quiz.questions.map((question, idx) => (
                <QuestionCard
                  key={idx}
                  question={question}
                  questionIndex={idx}
                  answer={answers[idx] || ''}
                  onAnswerChange={handleAnswerChange}
                />
              ))}
            </div>

            <button
              onClick={handleSubmitQuiz}
              disabled={loading}
              className="w-full mt-8 btn-primary flex items-center justify-center gap-3 text-lg py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
            >
              {loading ? (
                <>
                  <div className="spinner w-6 h-6 border-2" />
                  Submitting...
                </>
              ) : (
                <>
                  <Check className="w-6 h-6" />
                  Submit Quiz
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <QuizResults results={results} onNewQuiz={() => {
          setQuiz(null);
          setResults(null);
          setAnswers({});
        }} />
      )}
    </div>
  );
}

function QuestionCard({ question, questionIndex, answer, onAnswerChange }) {
  return (
    <div className="p-6 border-2 border-gray-200 rounded-2xl hover:border-primary/50 transition-all duration-200 bg-gradient-to-br from-white to-gray-50">
      <div className="flex items-start gap-4 mb-4">
        <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-primary to-secondary text-white rounded-xl flex items-center justify-center font-bold shadow-lg">
          {questionIndex + 1}
        </div>
        <div className="flex-1">
          <span className="inline-block px-3 py-1 text-xs font-bold bg-gradient-to-r from-blue-500 to-cyan-500 text-white rounded-full mb-3 shadow-md">
            {question.question_type}
          </span>
          <p className="text-gray-900 font-medium text-lg leading-relaxed">{question.question}</p>
        </div>
      </div>

      {question.question_type === 'MCQ' && question.options ? (
        <div className="space-y-3 ml-14">
          {question.options.map((option, idx) => (
            <label
              key={idx}
              className={`
                flex items-center p-4 rounded-xl cursor-pointer border-2 transition-all duration-200
                ${answer === option
                  ? 'border-primary bg-gradient-to-r from-primary/10 to-secondary/10 shadow-md scale-105'
                  : 'border-gray-200 hover:border-primary/50 hover:bg-gray-50'
                }
              `}
            >
              <input
                type="radio"
                name={`question-${questionIndex}`}
                value={option}
                checked={answer === option}
                onChange={(e) => onAnswerChange(questionIndex, e.target.value)}
                className="mr-4 w-5 h-5"
              />
              <span className="text-gray-900 font-medium">{option}</span>
            </label>
          ))}
        </div>
      ) : (
        <div className="ml-14">
          <textarea
            value={answer}
            onChange={(e) => onAnswerChange(questionIndex, e.target.value)}
            placeholder="Type your answer here..."
            rows={question.question_type === 'LAQ' ? 6 : 3}
            className="w-full px-5 py-4 border-2 border-gray-200 rounded-xl input-focus resize-none font-medium"
          />
        </div>
      )}
    </div>
  );
}

function QuizResults({ results, onNewQuiz }) {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100 fade-in">
      {/* Score Summary */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 mb-4">
          <Award className="w-8 h-8 text-yellow-500" />
          <h2 className="text-3xl font-bold text-gray-900">Quiz Results</h2>
        </div>
        <div className="relative inline-flex items-center justify-center w-40 h-40 mb-6">
          <div className="absolute inset-0 bg-gradient-to-br from-primary to-secondary rounded-full opacity-20 animate-pulse"></div>
          <div className="relative w-36 h-36 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-2xl">
            <span className="text-5xl font-bold text-white">
              {formatScore(results.score_percentage)}
            </span>
          </div>
        </div>
        <p className="text-xl text-gray-600 font-medium mb-2">
          You got <span className="text-primary font-bold">{results.correct_answers}</span> out of <span className="font-bold">{results.total_questions}</span> correct
        </p>
        <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-full border border-green-200">
          <TrendingUp className="w-5 h-5 text-green-600" />
          <span className="font-semibold text-green-700">
            {results.score_percentage >= 80 ? 'Excellent Work!' : results.score_percentage >= 60 ? 'Good Job!' : 'Keep Practicing!'}
          </span>
        </div>
      </div>

      {/* Detailed Results */}
      <div className="space-y-4 mb-8">
        {results.results.map((result, idx) => (
          <div
            key={idx}
            className={`
              p-6 rounded-2xl border-2 transition-all duration-200
              ${result.is_correct 
                ? 'border-green-300 bg-gradient-to-br from-green-50 to-emerald-50' 
                : 'border-red-300 bg-gradient-to-br from-red-50 to-rose-50'}
            `}
          >
            <div className="flex items-start gap-4">
              <div className={`
                flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center font-semibold shadow-lg
                ${result.is_correct 
                  ? 'bg-gradient-to-br from-green-500 to-emerald-500' 
                  : 'bg-gradient-to-br from-red-500 to-rose-500'}
              `}>
                {result.is_correct ? <Check className="w-6 h-6 text-white" /> : <X className="w-6 h-6 text-white" />}
              </div>
              <div className="flex-1">
                <p className="font-bold text-gray-900 mb-3 text-lg">{result.question}</p>
                
                <div className="space-y-3 text-sm">
                  <div className="flex items-start gap-2">
                    <span className="font-bold text-gray-700 min-w-[110px]">Your answer:</span>
                    <span className={`font-medium ${result.is_correct ? 'text-green-700' : 'text-red-700'}`}>
                      {result.user_answer || '(No answer)'}
                    </span>
                  </div>
                  
                  {!result.is_correct && (
                    <div className="flex items-start gap-2">
                      <span className="font-bold text-gray-700 min-w-[110px]">Correct answer:</span>
                      <span className="text-green-700 font-medium">{result.correct_answer}</span>
                    </div>
                  )}
                  
                  <div className="mt-4 p-4 bg-white rounded-xl border-2 border-gray-200">
                    <div className="flex items-start gap-2">
                      <Sparkles className="w-5 h-5 text-primary flex-shrink-0" />
                      <div>
                        <span className="font-bold text-gray-700 block mb-1">Explanation:</span>
                        <p className="text-gray-600 leading-relaxed">{result.explanation}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={onNewQuiz}
        className="w-full btn-primary flex items-center justify-center gap-3 text-lg py-4"
      >
        <RefreshCw className="w-6 h-6" />
        Generate New Quiz
      </button>
    </div>
  );
}

// ============================================================================
// CHAT PAGE
// ============================================================================
export function ChatPage() {
  const [pdfs, setPdfs] = useState([]);
  const [selectedPdf, setSelectedPdf] = useState(null);
  const [chats, setChats] = useState([]);
  const [currentChat, setCurrentChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [chatToDelete, setChatToDelete] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadPDFs();
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadPDFs = async () => {
    try {
      const data = await api.listPDFs();
      setPdfs(data.pdfs);
    } catch (error) {
      console.error('Failed to load PDFs:', error);
    }
  };

  const loadChatHistory = async () => {
    try {
      const data = await api.getChatHistory();
      setChats(data.chats);
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const loadChat = async (chatId) => {
    try {
      const data = await api.getChat(chatId);
      setCurrentChat(chatId);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to load chat:', error);
    }
  };

  const handleNewChat = () => {
    setCurrentChat(null);
    setMessages([]);
    setInput('');
  };

  const handleDeleteClick = (chat, e) => {
    e.stopPropagation();
    setChatToDelete(chat);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    if (!chatToDelete) return;
    
    setDeleting(chatToDelete.chat_id);
    try {
      await api.deleteChat(chatToDelete.chat_id);
      
      // If we deleted the current chat, clear it
      if (currentChat === chatToDelete.chat_id) {
        setCurrentChat(null);
        setMessages([]);
      }
      
      await loadChatHistory();
      setShowDeleteModal(false);
      setChatToDelete(null);
    } catch (error) {
      alert('Failed to delete chat: ' + error.message);
    } finally {
      setDeleting(null);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteModal(false);
    setChatToDelete(null);
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);

    setLoading(true);
    try {
      const data = await api.sendChatMessage(
        userMessage,
        currentChat,
        selectedPdf?.pdf_id
      );
      
      setCurrentChat(data.chat_id);
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.message,
        citations: data.citations,
        timestamp: new Date().toISOString()
      }]);

      await loadChatHistory();
    } catch (error) {
      alert('Failed to send message: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6 fade-in">
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 fade-in">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900">Delete Chat?</h2>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this conversation? This action cannot be undone.
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={handleDeleteCancel}
                className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-xl font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={deleting === chatToDelete?.chat_id}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-red-600 to-red-500 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deleting === chatToDelete?.chat_id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Left Sidebar - Chat History */}
      <div className="lg:col-span-1 bg-white rounded-2xl shadow-xl p-5 overflow-y-auto border border-gray-100">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Conversations</h2>
            <p className="text-xs text-gray-500">{chats.length} chats</p>
          </div>
          <button
            onClick={handleNewChat}
            className="p-2 bg-gradient-to-br from-primary to-secondary text-white rounded-xl hover:shadow-lg transition-all duration-200 hover:scale-110"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* PDF Selector */}
        <div className="mb-5">
          <label className="block text-xs font-bold text-gray-700 mb-2">
            📚 Context Document
          </label>
          <select
            value={selectedPdf?.pdf_id || ''}
            onChange={(e) => {
              const pdf = pdfs.find(p => p.pdf_id === e.target.value);
              setSelectedPdf(pdf || null);
            }}
            className="w-full px-3 py-2 text-sm border-2 border-gray-200 rounded-xl input-focus font-medium"
          >
            <option value="">No PDF</option>
            {pdfs.map((pdf) => (
              <option key={pdf.pdf_id} value={pdf.pdf_id}>
                {truncateText(pdf.filename, 30)}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          {chats.map((chat) => (
            <div
              key={chat.chat_id}
              onClick={() => loadChat(chat.chat_id)}
              className={`
                group relative p-3 rounded-xl cursor-pointer border-2 transition-all duration-200
                ${currentChat === chat.chat_id
                  ? 'border-primary bg-gradient-to-r from-primary/10 to-secondary/10 shadow-md'
                  : 'border-gray-200 hover:border-primary/50 hover:shadow-sm'
                }
              `}
            >
              <div className="flex items-start gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate mb-1">
                    {truncateText(chat.last_message, 35)}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <MessageCircle className="w-3 h-3" />
                    <span>{chat.message_count} messages</span>
                  </div>
                </div>
                
                {/* Delete Button */}
                <button
                  onClick={(e) => handleDeleteClick(chat, e)}
                  disabled={deleting === chat.chat_id}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-red-100 rounded-lg disabled:opacity-50 flex-shrink-0"
                  title="Delete chat"
                >
                  <Trash2 className="w-3.5 h-3.5 text-red-600" />
                </button>
              </div>
            </div>
          ))}
          {chats.length === 0 && (
            <div className="text-center py-8">
              <MessageCircle className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm text-gray-500">No conversations yet</p>
              <p className="text-xs text-gray-400 mt-1">Start chatting to begin!</p>
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="lg:col-span-3 bg-white rounded-2xl shadow-xl flex flex-col border border-gray-100 overflow-hidden">
        {/* Chat Header */}
        <div className="p-5 border-b bg-gradient-to-r from-purple-50 to-pink-50">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
              <MessageCircle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                AI Teacher Assistant
              </h2>
              {selectedPdf && (
                <p className="text-sm text-gray-600">
                  📖 {truncateText(selectedPdf.filename, 40)}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-br from-gray-50 to-white">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center">
                  <MessageCircle className="w-12 h-12 text-purple-600" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Start a Conversation</h3>
                <p className="text-gray-600 mb-6">Ask me anything about your coursebook!</p>
                <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
                  <button className="px-4 py-2 bg-white border-2 border-purple-200 rounded-xl hover:border-purple-400 transition-colors text-sm">
                    💡 Explain this concept
                  </button>
                  <button className="px-4 py-2 bg-white border-2 border-purple-200 rounded-xl hover:border-purple-400 transition-colors text-sm">
                    🔍 Give me examples
                  </button>
                  <button className="px-4 py-2 bg-white border-2 border-purple-200 rounded-xl hover:border-purple-400 transition-colors text-sm">
                    🎯 Practice questions
                  </button>
                </div>
              </div>
            </div>
          ) : (
            messages.map((message, idx) => (
              <MessageBubble key={idx} message={message} />
            ))
          )}
          {loading && (
            <div className="flex items-center gap-3 p-4 bg-white rounded-2xl shadow-md w-fit">
              <div className="spinner w-5 h-5 border-2" />
              <span className="text-gray-600 font-medium">AI is thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-5 border-t bg-gray-50">
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              rows={2}
              className="flex-1 px-5 py-4 border-2 border-gray-200 rounded-2xl input-focus resize-none font-medium"
              disabled={loading}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="px-8 bg-gradient-to-br from-purple-600 to-pink-600 text-white rounded-2xl hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95"
            >
              <Send className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} fade-in`}>
      <div className={`
        max-w-[80%] rounded-2xl p-5 shadow-lg
        ${isUser 
          ? 'bg-gradient-to-br from-primary to-secondary text-white' 
          : 'bg-white text-gray-900 border border-gray-200'
        }
      `}>
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
        
        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-300/30">
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4" />
              <p className="text-xs font-bold">Sources:</p>
            </div>
            {message.citations.map((citation, idx) => (
              <div key={idx} className="text-xs mb-3 p-3 bg-white/10 rounded-xl backdrop-blur-sm">
                <p className="font-bold mb-1">📄 Page {citation.page}</p>
                <p className="italic opacity-90">"{citation.snippet}"</p>
              </div>
            ))}
          </div>
        )}
        
        <p className="text-xs mt-3 opacity-70">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// PROGRESS PAGE
// ============================================================================
export function ProgressPage() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      const data = await api.getProgress();
      setProgress(data);
    } catch (error) {
      console.error('Failed to load progress:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner w-12 h-12" />
      </div>
    );
  }

  if (!progress || progress.total_quizzes === 0) {
    return (
      <div className="max-w-4xl mx-auto fade-in">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">Progress Dashboard</h1>
        <div className="bg-white rounded-2xl shadow-xl p-12 text-center border border-gray-100">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-green-100 to-emerald-100 rounded-full flex items-center justify-center">
            <BarChart3 className="w-12 h-12 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Start Your Journey</h2>
          <p className="text-gray-600 mb-8 text-lg">
            Take your first quiz to unlock insights and track your learning progress!
          </p>
          <a
            href="/quiz"
            className="inline-flex items-center gap-3 btn-primary text-lg"
          >
            <Sparkles className="w-6 h-6" />
            Start First Quiz
          </a>
        </div>
      </div>
    );
  }

  const chartData = progress.recent_attempts.map((attempt, idx) => ({
    name: `Quiz ${progress.recent_attempts.length - idx}`,
    score: attempt.score,
  })).reverse();

  return (
    <div className="max-w-6xl mx-auto fade-in">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Progress Dashboard</h1>
            <p className="text-gray-500">Track your learning journey and achievements</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Total Quizzes"
          value={progress.total_quizzes}
          icon={FileText}
          gradient="from-blue-500 to-cyan-500"
        />
        <StatCard
          title="Questions Answered"
          value={progress.total_questions_answered}
          icon={Check}
          gradient="from-green-500 to-emerald-500"
        />
        <StatCard
          title="Overall Score"
          value={formatScore(progress.overall_score)}
          icon={Award}
          gradient="from-purple-500 to-pink-500"
        />
      </div>

      {/* Chart */}
      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-primary" />
          Performance Trend
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" stroke="#6b7280" />
            <YAxis domain={[0, 100]} stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="score" 
              stroke="url(#colorGradient)" 
              strokeWidth={3}
              name="Score (%)"
              dot={{ fill: '#6366f1', strokeWidth: 2, r: 6 }}
              activeDot={{ r: 8 }}
            />
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-xl p-8 border-2 border-green-200">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg">
              <Check className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-green-900">Strengths</h2>
          </div>
          {progress.strengths.length > 0 ? (
            <ul className="space-y-3">
              {progress.strengths.map((strength, idx) => (
                <li key={idx} className="flex items-center gap-3 text-gray-800 bg-white p-4 rounded-xl shadow-sm">
                  <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span className="font-medium">{strength}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-600">Keep taking quizzes to identify your strengths!</p>
          )}
        </div>

        <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl shadow-xl p-8 border-2 border-orange-200">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center shadow-lg">
              <Target className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-red-900">Focus Areas</h2>
          </div>
          {progress.weaknesses.length > 0 ? (
            <ul className="space-y-3">
              {progress.weaknesses.map((weakness, idx) => (
                <li key={idx} className="flex items-center gap-3 text-gray-800 bg-white p-4 rounded-xl shadow-sm">
                  <Target className="w-5 h-5 text-orange-600 flex-shrink-0" />
                  <span className="font-medium">{weakness}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-3 text-green-700 bg-white p-4 rounded-xl shadow-sm">
              <Award className="w-6 h-6 flex-shrink-0" />
              <span className="font-medium">Great! No major weaknesses identified.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, gradient }) {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 card-hover">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-semibold mb-2">{title}</p>
          <p className="text-4xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
          <Icon className="w-8 h-8 text-white" />
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// YOUTUBE PAGE
// ============================================================================
export function YouTubePage() {
  const [topic, setTopic] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleGetRecommendations = async () => {
    if (!topic.trim()) return;

    setLoading(true);
    try {
      const data = await api.getYouTubeRecommendations(topic);
      setRecommendations(data.recommendations);
    } catch (error) {
      alert('Failed to get recommendations: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleGetRecommendations();
    }
  };

  return (
    <div className="max-w-4xl mx-auto fade-in">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-rose-600 rounded-xl flex items-center justify-center shadow-lg">
            <Youtube className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Video Recommendations</h1>
            <p className="text-gray-500">AI-powered educational video suggestions</p>
          </div>
        </div>
      </div>

      {/* Search Box */}
      <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
        <label className="block text-lg font-bold text-gray-900 mb-4">
          🎯 What topic would you like to learn?
        </label>
        <div className="flex gap-3"></div>
        <div className="flex gap-3">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., Newton's Laws of Motion"
            className="flex-1 px-5 py-4 border-2 border-gray-200 rounded-xl input-focus font-medium text-lg"
          />
          <button
            onClick={handleGetRecommendations}
            disabled={loading || !topic.trim()}
            className="px-8 bg-gradient-to-r from-red-600 to-rose-600 text-white rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95 font-semibold"
          >
            {loading ? (
              <div className="spinner w-6 h-6 border-2" />
            ) : (
              <Youtube className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="space-y-4 fade-in">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-red-600" />
            Recommended Videos
          </h2>
          {recommendations.map((video, idx) => (
            <div
              key={idx}
              className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-200 border border-gray-100 card-hover"
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-14 h-14 bg-gradient-to-br from-red-600 to-rose-600 rounded-xl flex items-center justify-center shadow-lg">
                  <Youtube className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {video.title}
                  </h3>
                  <div className="flex items-center gap-3 mb-3">
                    <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
                      {video.channel}
                    </span>
                    <span className="text-gray-500 text-sm">•</span>
                    <span className="text-gray-600 text-sm">Educational Content</span>
                  </div>
                  <p className="text-gray-600 leading-relaxed">
                    <span className="font-semibold text-gray-700">Why recommended:</span> {video.reason}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {recommendations.length === 0 && !loading && (
        <div className="bg-white rounded-2xl shadow-xl p-12 text-center border border-gray-100">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-red-100 to-rose-100 rounded-full flex items-center justify-center">
            <Youtube className="w-12 h-12 text-red-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Discover Learning Videos</h3>
          <p className="text-gray-600 mb-6">
            Enter any topic and get AI-curated educational video recommendations from top channels
          </p>
          <div className="flex flex-wrap gap-2 justify-center">
            <button
              onClick={() => setTopic("Photosynthesis")}
              className="px-4 py-2 bg-white border-2 border-red-200 rounded-xl hover:border-red-400 transition-colors text-sm font-medium"
            >
              🌿 Photosynthesis
            </button>
            <button
              onClick={() => setTopic("Trigonometry")}
              className="px-4 py-2 bg-white border-2 border-red-200 rounded-xl hover:border-red-400 transition-colors text-sm font-medium"
            >
              📐 Trigonometry
            </button>
            <button
              onClick={() => setTopic("World War 2")}
              className="px-4 py-2 bg-white border-2 border-red-200 rounded-xl hover:border-red-400 transition-colors text-sm font-medium"
            >
              🌍 World War 2
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
