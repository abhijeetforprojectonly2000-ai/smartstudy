import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// PDF APIs
export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/pdf/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const listPDFs = async () => {
  const response = await api.get('/api/pdf/list');
  return response.data;
};

export const getPDFFile = (pdfId) => {
  return `${API_BASE_URL}/api/pdf/${pdfId}`;
};

export const getPDFText = async (pdfId) => {
  const response = await api.get(`/api/pdf/${pdfId}/text`);
  return response.data;
};

// Quiz APIs
export const generateQuiz = async (pdfId, numMcq = 5, numSaq = 3, numLaq = 2) => {
  const response = await api.post('/api/quiz/generate', {
    pdf_id: pdfId,
    num_mcq: numMcq,
    num_saq: numSaq,
    num_laq: numLaq,
  });
  return response.data;
};

export const submitQuiz = async (quizId, answers) => {
  const response = await api.post('/api/quiz/submit', {
    quiz_id: quizId,
    answers,
  });
  return response.data;
};

// Chat APIs
export const sendChatMessage = async (message, chatId = null, pdfId = null) => {
  const response = await api.post('/api/chat', {
    message,
    chat_id: chatId,
    pdf_id: pdfId,
  });
  return response.data;
};

export const getChatHistory = async () => {
  const response = await api.get('/api/chat/history');
  return response.data;
};

export const getChat = async (chatId) => {
  const response = await api.get(`/api/chat/${chatId}`);
  return response.data;
};

// Progress APIs
export const getProgress = async () => {
  const response = await api.get('/api/progress');
  return response.data;
};

// YouTube Recommendation APIs
export const getYouTubeRecommendations = async (topic, pdfId = null) => {
  const response = await api.post('/api/recommend/youtube', {
    topic,
    pdf_id: pdfId,
  });
  return response.data;
};

export default api;