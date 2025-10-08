import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, BookOpen, MessageSquare, BarChart3, Youtube, Menu, X, GraduationCap, Sparkles } from 'lucide-react';
import { 
  HomePage, 
  QuizPage, 
  ChatPage, 
  ProgressPage, 
  YouTubePage 
} from './components';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
        <Layout />
      </div>
    </Router>
  );
}

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Home', href: '/', icon: Home },
    { name: 'Quiz', href: '/quiz', icon: BookOpen },
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'Progress', href: '/progress', icon: BarChart3 },
    { name: 'YouTube', href: '/youtube', icon: Youtube },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-900/50 backdrop-blur-sm lg:hidden transition-opacity duration-300"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-72 bg-white/80 backdrop-blur-xl shadow-2xl 
        transform transition-transform duration-300 ease-in-out border-r border-gray-100
        lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-24 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/90 to-purple-600/90"></div>
            <div className="flex items-center gap-3 relative z-10">
              <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-lg transform hover:rotate-6 transition-transform">
                <GraduationCap className="w-7 h-7 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  SmartStudy
                  <Sparkles className="w-4 h-4" />
                </h1>
                <p className="text-xs text-indigo-100">AI Learning Assistant</p>
              </div>
            </div>
            <button 
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-white hover:bg-white/20 p-2 rounded-lg transition-colors relative z-10"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-8 space-y-2 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    group flex items-center px-4 py-3.5 rounded-xl transition-all duration-200
                    ${active
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-200'
                      : 'text-gray-700 hover:bg-gray-100 hover:shadow-md'
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 mr-3 transition-transform ${active ? '' : 'group-hover:scale-110'}`} />
                  <span className="font-medium">{item.name}</span>
                  {active && (
                    <div className="ml-auto w-2 h-2 bg-white rounded-full"></div>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-100">
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 mb-3 border border-indigo-100">
              <p className="text-xs font-semibold text-indigo-900 mb-1.5 flex items-center gap-1">
                💡 Quick Tip
              </p>
              <p className="text-xs text-gray-600 leading-relaxed">
                Upload your NCERT PDF to get started with AI-powered learning!
              </p>
            </div>
            <p className="text-xs text-gray-500 text-center">
              © 2025 SmartStudy
            </p>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile header */}
        <header className="lg:hidden bg-white/80 backdrop-blur-xl border-b border-gray-100 shadow-sm px-4 py-4 flex items-center justify-between">
          <button 
            onClick={() => setSidebarOpen(true)}
            className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
          >
            <Menu className="w-6 h-6" />
          </button>
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-indigo-600" />
            <h1 className="text-lg font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              BeyondStudy
            </h1>
          </div>
          <div className="w-10" /> {/* Spacer */}
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/quiz" element={<QuizPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/progress" element={<ProgressPage />} />
            <Route path="/youtube" element={<YouTubePage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;