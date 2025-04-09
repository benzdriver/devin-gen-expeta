import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Requirements from './pages/Requirements';
import Expectations from './pages/Expectations';
import CodeGeneration from './pages/CodeGeneration';
import Validation from './pages/Validation';
import Memory from './pages/Memory';
import Settings from './pages/Settings';
import SemanticMediator from './pages/SemanticMediator';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [sessionId, setSessionId] = useState(null);
  const [userData, setUserData] = useState({
    name: '张明',
    role: '系统管理员'
  });

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

  const renderActivePage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard sessionId={sessionId} />;
      case 'requirements':
        return <Requirements sessionId={sessionId} />;
      case 'expectations':
        return <Expectations sessionId={sessionId} />;
      case 'code-generation':
        return <CodeGeneration sessionId={sessionId} />;
      case 'validation':
        return <Validation sessionId={sessionId} />;
      case 'memory':
        return <Memory sessionId={sessionId} />;
      case 'semantic-mediator':
        return <SemanticMediator sessionId={sessionId} />;
      case 'settings':
        return <Settings userData={userData} setUserData={setUserData} />;
      default:
        return <Dashboard sessionId={sessionId} />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        activePage={activePage} 
        setActivePage={setActivePage} 
        userData={userData}
      />
      <main className="main-content">
        <Header 
          title={getPageTitle(activePage)} 
          sessionId={sessionId}
        />
        <div id={activePage} className="content-area page">
          {renderActivePage()}
        </div>
      </main>
    </div>
  );
}

function getPageTitle(page) {
  switch (page) {
    case 'dashboard': return '仪表盘';
    case 'requirements': return '需求管理';
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