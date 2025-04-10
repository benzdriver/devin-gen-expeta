import React, { useState, useEffect } from 'react';
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Requirements from './pages/Requirements';
import SimpleRequirements from './pages/SimpleRequirements';
import NativeRequirements from './pages/NativeRequirements';
import ChatRequirements from './pages/ChatRequirements';
import EnhancedChatRequirements from './pages/EnhancedChatRequirements';
import SimpleChat from './pages/SimpleChat';
import DirectChat from './pages/DirectChat';
import BasicChat from './pages/BasicChat';
import TestForm from './pages/TestForm';
import Expectations from './pages/Expectations';
import CodeGeneration from './pages/CodeGeneration';
import Validation from './pages/Validation';
import Memory from './pages/Memory';
import Settings from './pages/Settings';
import SemanticMediator from './pages/SemanticMediator';

export const API_BASE_URL = 'http://localhost:8000';

function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState(null);
  const [userData, setUserData] = useState({
    name: '张明',
    role: '系统管理员'
  });

  const getActivePageFromPath = () => {
    const path = location.pathname.replace('/', '');
    if (path === '') return 'dashboard';
    return path;
  };

  const activePage = getActivePageFromPath();

  useEffect(() => {
    const initApp = async () => {
      try {
        // 初始化会话
        const response = await fetch(`${API_BASE_URL}/chat/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            user_message: 'Hello',
            session_id: null
          }),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to create session: ${response.statusText}`);
        }
        
        const data = await response.json();
        setSessionId(data.session_id);
      } catch (error) {
        console.error('Error initializing app:', error);
      }
    };
    
    initApp();
  }, []);

  const handlePageChange = (pageId) => {
    navigate(`/${pageId === 'dashboard' ? '' : pageId}`);
  };

  return (
    <div className="app-container">
      <Sidebar 
        activePage={activePage} 
        setActivePage={handlePageChange} 
        userData={userData}
      />
      <main className="main-content">
        <Header 
          title={getPageTitle(activePage)} 
          sessionId={sessionId}
        />
        <div id={activePage} className="content-area page">
          <Routes>
            <Route path="/" element={<Dashboard sessionId={sessionId} />} />
            <Route path="/requirements" element={<ChatRequirements sessionId={sessionId} />} />
            <Route path="/simple-requirements" element={<SimpleRequirements />} />
            <Route path="/native-requirements" element={<NativeRequirements sessionId={sessionId} />} />
            <Route path="/old-requirements" element={<Requirements sessionId={sessionId} />} />
            <Route path="/chat-requirements" element={<EnhancedChatRequirements sessionId={sessionId} />} />
            <Route path="/simple-chat" element={<SimpleChat />} />
            <Route path="/direct-chat" element={<DirectChat />} />
            <Route path="/basic-chat" element={<BasicChat />} />
            <Route path="/expectations" element={<Expectations sessionId={sessionId} />} />
            <Route path="/code-generation" element={<CodeGeneration sessionId={sessionId} />} />
            <Route path="/validation" element={<Validation sessionId={sessionId} />} />
            <Route path="/memory" element={<Memory sessionId={sessionId} />} />
            <Route path="/semantic-mediator" element={<SemanticMediator sessionId={sessionId} />} />
            <Route path="/settings" element={<Settings userData={userData} setUserData={setUserData} />} />
            <Route path="/test-form" element={<TestForm />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

function getPageTitle(page) {
  switch (page) {
    case 'dashboard': return '仪表盘';
    case 'requirements': return '需求管理';
    case 'native-requirements': return '统一需求对话';
    case 'expectations': return '期望管理';
    case 'code-generation': return '代码生成';
    case 'validation': return '验证结果';
    case 'memory': return '记忆系统';
    case 'semantic-mediator': return '语义中介层';
    case 'settings': return '系统设置';
    default: return '仪表盘';
  }
}

export default App;                                      