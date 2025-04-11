import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../App';
import '../requirements.css';
import '../chat-input.css';

function ChatRequirements({ sessionId }) {
  const navigate = useNavigate();
  const [chatMessages, setChatMessages] = useState([
    { 
      role: 'system', 
      content: '欢迎使用Expeta 2.0! 我是您的产品经理，请告诉我您想要构建什么样的系统？我会帮您澄清需求并生成期望模型。',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [expectationData, setExpectationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [activeStep, setActiveStep] = useState(1);
  const [generationProgress, setGenerationProgress] = useState(null);
  const [tokenUsage, setTokenUsage] = useState({
    total: 1000000,
    used: 0,
    available: 1000000
  });
  const [userInput, setUserInput] = useState('');
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  
  console.log('ChatRequirements component rendering with sessionId:', sessionId);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, isTyping]);
  
  useEffect(() => {
    const fetchTokenUsage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/token/usage`);
        if (response.ok) {
          const data = await response.json();
          setTokenUsage({
            total: data.total_tokens || 1000000,
            used: data.used_tokens || 0,
            available: data.available_tokens || 1000000
          });
        }
      } catch (error) {
        console.error('Error fetching token usage:', error);
      }
    };
    
    fetchTokenUsage();
    const interval = setInterval(fetchTokenUsage, 60000); // 每分钟更新一次
    
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (message) => {
    if (!message.trim()) {
      console.log('Empty message, not sending');
      return;
    }
    
    console.log('Sending message:', message);
    
    const newUserMessage = {
      role: 'user',
      content: message,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setChatMessages(prev => [...prev, newUserMessage]);
    setIsTyping(true);
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/chat/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: message,
          session_id: conversationId || sessionId || 'session_' + Math.random().toString(36).substring(2, 15)
        }),
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('API response:', data);
      
      if (data.session_id && !conversationId) {
        setConversationId(data.session_id);
        console.log('Conversation ID set:', data.session_id);
      }
      
      if (data.expectation) {
        setExpectationData(data.expectation);
        
        if (data.stage === 'completed') {
          setActiveStep(3);
        } else if (data.stage === 'awaiting_details' || data.stage === 'refining') {
          setActiveStep(2);
        }
      }
      
      const formattedContent = formatMarkdown(data.response || '我需要更多信息来理解您的需求。请提供更多细节。');
      
      const systemMessage = {
        role: 'system',
        content: formattedContent,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        rawContent: data.response
      };
      
      setChatMessages(prev => [...prev, systemMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'system',
        content: '抱歉，发生了错误。请稍后再试。',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setLoading(false);
    }
  };
  
  const handleFormSubmit = (event) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    console.log('Form submitted with input:', userInput);
    
    if (userInput.trim()) {
      handleSendMessage(userInput);
      setUserInput('');
    }
    
    return false;
  };
  
  const formatMarkdown = (content) => {
    if (!content) return '';
    
    let formatted = content
      .replace(/## (.*?)$/gm, '<h3>$1</h3>')
      .replace(/### (.*?)$/gm, '<h4>$1</h4>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
    
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    formatted = formatted.replace(/^\d+\. (.*?)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/^- (.*?)$/gm, '<li>$1</li>');
    
    formatted = formatted.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');
    
    return formatted;
  };
  
  const handleGenerateCode = async () => {
    if (!expectationData || !expectationData.top_level_expectation) {
      alert('请先完成需求澄清，生成期望模型');
      return;
    }
    
    setLoading(true);
    setGenerationProgress({
      status: 'starting',
      message: '正在准备代码生成...',
      progress: 0
    });
    
    try {
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          expectation_id: expectationData.top_level_expectation.id,
          session_id: sessionId
        }),
      });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Generation started:', data);
      
      const systemMessage = {
        role: 'system',
        content: '代码生成已开始，请稍候...',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setChatMessages(prev => [...prev, systemMessage]);
      
      setActiveStep(4);
      
      pollGenerationProgress();
    } catch (error) {
      console.error('Error starting code generation:', error);
      
      const errorMessage = {
        role: 'system',
        content: '启动代码生成失败，请重试。',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
      setGenerationProgress(null);
    } finally {
      setLoading(false);
    }
  };
  
  const pollGenerationProgress = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/generation/status?session_id=${sessionId}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Generation progress:', data);
        
        setGenerationProgress({
          status: data.status,
          message: data.message || '正在生成代码...',
          progress: data.progress || 0,
          files: data.files || []
        });
        
        if (data.status === 'completed') {
          const completionMessage = {
            role: 'system',
            content: `代码生成已完成！共生成了 ${data.files?.length || 0} 个文件。您可以下载生成的代码包。`,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          
          setChatMessages(prev => [...prev, completionMessage]);
          setActiveStep(5);
        } else if (data.status === 'failed') {
          const failureMessage = {
            role: 'system',
            content: `代码生成失败：${data.message || '未知错误'}`,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          
          setChatMessages(prev => [...prev, failureMessage]);
        } else {
          setTimeout(pollGenerationProgress, 3000);
        }
      } else {
        throw new Error(`API request failed: ${response.status}`);
      }
    } catch (error) {
      console.error('Error polling generation progress:', error);
      
      const errorMessage = {
        role: 'system',
        content: '获取生成进度失败，但生成可能仍在进行中。',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
    }
  };
  
  const handleDownloadCode = async () => {
    if (!sessionId) return;
    
    try {
      window.open(`${API_BASE_URL}/download/code/${sessionId}`, '_blank');
    } catch (error) {
      console.error('Error downloading code:', error);
      alert('下载代码失败，请重试');
    }
  };
  
  const handleDownloadExpectation = async () => {
    if (!expectationData || !expectationData.top_level_expectation) return;
    
    try {
      window.open(`${API_BASE_URL}/download/expectation/${expectationData.top_level_expectation.id}`, '_blank');
    } catch (error) {
      console.error('Error downloading expectation:', error);
      alert('下载期望模型失败，请重试');
    }
  };
  
  const handleRestartConversation = () => {
    if (window.confirm('确定要重新开始对话吗？当前的对话内容将不会保存。')) {
      setConversationId(null);
      setActiveStep(1);
      setExpectationData(null);
      setGenerationProgress(null);
      setChatMessages([{
        role: 'system',
        content: '让我们重新开始。请告诉我您想要构建的系统或功能。',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    }
  };

  return (
    <div className="requirements-page">
      {/* 工作流程可视化 */}
      <section className="workflow-section">
        <div className="section-header">
          <h2>处理流程</h2>
          <div className="section-actions">
            <button 
              className="secondary-button" 
              onClick={handleRestartConversation}
              title="重新开始对话"
              disabled={loading}
            >
              <span className="material-symbols-rounded">refresh</span>
              <span>重新开始</span>
            </button>
          </div>
        </div>
        <div className="workflow-visualization">
          <div className={`workflow-step ${activeStep >= 1 ? 'active' : ''}`}>
            <div className="step-icon">
              <span className="material-symbols-rounded">description</span>
            </div>
            <div className="step-label">需求输入</div>
            <div className="step-connector"></div>
          </div>
          <div className={`workflow-step ${activeStep >= 2 ? 'active' : activeStep === 1 ? 'in-progress' : ''}`}>
            <div className="step-icon">
              <span className="material-symbols-rounded">psychology</span>
            </div>
            <div className="step-label">需求澄清</div>
            <div className="step-connector"></div>
          </div>
          <div className={`workflow-step ${activeStep >= 3 ? 'active' : activeStep === 2 ? 'in-progress' : ''}`}>
            <div className="step-icon">
              <span className="material-symbols-rounded">format_list_bulleted</span>
            </div>
            <div className="step-label">期望生成</div>
            <div className="step-connector"></div>
          </div>
          <div className={`workflow-step ${activeStep >= 4 ? 'active' : activeStep === 3 ? 'in-progress' : ''}`}>
            <div className="step-icon">
              <span className="material-symbols-rounded">code</span>
            </div>
            <div className="step-label">代码生成</div>
            <div className="step-connector"></div>
          </div>
          <div className={`workflow-step ${activeStep >= 5 ? 'active' : activeStep === 4 ? 'in-progress' : ''}`}>
            <div className="step-icon">
              <span className="material-symbols-rounded">verified</span>
            </div>
            <div className="step-label">代码验证</div>
          </div>
        </div>
      </section>
      
      <div className="requirements-container">
        {/* 聊天交互区域 */}
        <section className="chat-section">
          <div className="section-header">
            <h2>需求交互</h2>
            <div className="section-actions">
              {activeStep >= 3 && (
                <button 
                  className="secondary-button" 
                  onClick={handleDownloadExpectation}
                  disabled={loading || !expectationData}
                  title="下载期望模型"
                >
                  <span className="material-symbols-rounded">download</span>
                  <span>导出期望</span>
                </button>
              )}
              {activeStep >= 3 && (
                <button 
                  className="primary-button" 
                  onClick={handleGenerateCode}
                  disabled={loading || !expectationData || activeStep >= 4}
                >
                  <span className="material-symbols-rounded">code</span>
                  <span>生成代码</span>
                </button>
              )}
              {activeStep >= 5 && (
                <button 
                  className="primary-button" 
                  onClick={handleDownloadCode}
                  disabled={loading}
                >
                  <span className="material-symbols-rounded">download</span>
                  <span>下载代码</span>
                </button>
              )}
            </div>
          </div>
          
          {/* Token使用情况 */}
          <div className="token-usage">
            <div className="token-label">Token使用情况:</div>
            <div className="token-progress">
              <div 
                className="token-progress-bar" 
                style={{ width: `${(tokenUsage.used / tokenUsage.total) * 100}%` }}
              ></div>
            </div>
            <div className="token-stats">
              <span>已用: {tokenUsage.used.toLocaleString()}</span>
              <span>可用: {tokenUsage.available.toLocaleString()}</span>
              <span>总量: {tokenUsage.total.toLocaleString()}</span>
            </div>
          </div>
          
          <div className="chat-container" ref={chatContainerRef}>
            <div className="chat-messages">
              {chatMessages.map((msg, index) => (
                <div 
                  key={index} 
                  className={`message ${msg.role === 'user' ? 'user-message' : 'system-message'}`}
                >
                  <div className="message-content">
                    {msg.role === 'user' ? (
                      <p>{msg.content}</p>
                    ) : (
                      <div dangerouslySetInnerHTML={{ __html: msg.content }} />
                    )}
                  </div>
                  <div className="message-time">{msg.time}</div>
                </div>
              ))}
              
              {isTyping && (
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              )}
              
              {generationProgress && (
                <div className="generation-progress">
                  <h4>代码生成进度</h4>
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar" 
                      style={{ width: (generationProgress.progress || 0) + '%' }}
                    ></div>
                  </div>
                  <div className="progress-status">
                    {generationProgress.message} ({generationProgress.progress || 0}%)
                  </div>
                  {generationProgress.files && generationProgress.files.length > 0 && (
                    <div className="generated-files">
                      <h5>已生成文件:</h5>
                      <ul>
                        {generationProgress.files.slice(0, 5).map((file, idx) => (
                          <li key={idx}>{file}</li>
                        ))}
                        {generationProgress.files.length > 5 && (
                          <li>...以及 {generationProgress.files.length - 5} 个其他文件</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
            
            <div className="chat-input-container">
              <form onSubmit={(e) => {
                e.preventDefault();
                console.log('Form submitted with input:', userInput);
                handleFormSubmit();
              }}>
                <div className="input-wrapper">
                  <textarea 
                    name="user-message"
                    id="user-message"
                    placeholder="请描述您的需求..."
                    disabled={loading}
                    autoComplete="off"
                    value={userInput}
                    onChange={(e) => {
                      console.log('Input changed:', e.target.value);
                      setUserInput(e.target.value);
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey && !loading) {
                        e.preventDefault();
                        console.log('Enter key pressed, submitting form');
                        handleFormSubmit();
                      }
                    }}
                    onInput={(e) => {
                      console.log('Input event fired:', e.target.value);
                    }}
                    rows="2"
                    style={{ resize: 'vertical', minHeight: '40px' }}
                  />
                  <button 
                    type="submit"
                    className="send-button"
                    disabled={loading}
                  >
                    <span className="material-symbols-rounded">send</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default ChatRequirements;
