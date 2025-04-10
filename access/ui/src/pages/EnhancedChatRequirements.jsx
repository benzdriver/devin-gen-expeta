import React, { useState, useEffect, useRef } from 'react';
import '../chat-input.css';

const API_BASE_URL = 'http://localhost:8000';

function EnhancedChatRequirements({ sessionId: initialSessionId }) {
  const [chatMessages, setChatMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(initialSessionId || null);
  const [expectationId, setExpectationId] = useState(null);
  const [generationId, setGenerationId] = useState(null);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationStatus, setGenerationStatus] = useState('idle');
  const [tokenUsage, setTokenUsage] = useState({
    total: 0,
    used: 0,
    available: 0
  });
  const [debugInfo, setDebugInfo] = useState({
    lastAction: 'none',
    inputValue: '',
    buttonState: 'enabled'
  });

  const textareaRef = useRef(null);
  const sendButtonRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const fetchTokenUsage = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/token/usage`);
        if (response.ok) {
          const data = await response.json();
          setTokenUsage({
            total: data.total || 0,
            used: data.used || 0,
            available: data.available || 0
          });
        }
      } catch (error) {
        console.error('Error fetching token usage:', error);
      }
    };

    fetchTokenUsage();
    const interval = setInterval(fetchTokenUsage, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (chatMessages.length === 0) {
      setChatMessages([
        {
          role: 'assistant',
          content: '欢迎使用Expeta 2.0! 我是您的需求分析助手。请告诉我您想要构建的系统或功能，我会帮您澄清需求并生成期望模型。',
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    }
  }, [chatMessages]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  useEffect(() => {
    const textarea = textareaRef.current;
    const sendButton = sendButtonRef.current;

    if (textarea && sendButton) {
      console.log('Initializing textarea and send button with event listeners');

      const newTextarea = textarea.cloneNode(true);
      const newButton = sendButton.cloneNode(true);
      
      if (textarea.parentNode) {
        textarea.parentNode.replaceChild(newTextarea, textarea);
      }
      
      if (sendButton.parentNode) {
        sendButton.parentNode.replaceChild(newButton, sendButton);
      }
      
      textareaRef.current = newTextarea;
      sendButtonRef.current = newButton;
      
      newTextarea.addEventListener('input', function(e) {
        console.log('Input event fired:', e.target.value);
        const hasContent = e.target.value.trim().length > 0;
        
        if (newButton) {
          newButton.disabled = loading || !hasContent;
          newButton.style.opacity = (loading || !hasContent) ? '0.5' : '1';
          newButton.style.cursor = (loading || !hasContent) ? 'not-allowed' : 'pointer';
        }
        
        setDebugInfo(prev => ({
          ...prev,
          inputValue: e.target.value,
          buttonState: (loading || !hasContent) ? 'disabled' : 'enabled'
        }));
      });
      
      newTextarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && !loading) {
          const currentValue = e.target.value.trim();
          if (currentValue) {
            e.preventDefault();
            console.log('Enter key pressed, submitting with:', currentValue);
            
            const inputToSend = currentValue;
            e.target.value = '';
            
            if (newButton) {
              newButton.disabled = true;
              newButton.style.opacity = '0.5';
              newButton.style.cursor = 'not-allowed';
            }
            
            setDebugInfo(prev => ({
              ...prev,
              lastAction: `Enter key pressed, sending: ${inputToSend}`,
              inputValue: '',
              buttonState: 'disabled'
            }));
            
            handleSendMessage(inputToSend);
          }
        }
      });
      
      newButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Send button clicked via direct event listener');
        
        if (!newTextarea) {
          console.error('Textarea element not found');
          return;
        }
        
        const currentValue = newTextarea.value.trim();
        console.log('Current textarea value:', currentValue);
        
        if (currentValue && !loading) {
          console.log('Sending message with input:', currentValue);
          const inputToSend = currentValue;
          newTextarea.value = '';
          
          newButton.disabled = true;
          newButton.style.opacity = '0.5';
          newButton.style.cursor = 'not-allowed';
          
          setDebugInfo(prev => ({
            ...prev,
            lastAction: `Button clicked, sending: ${inputToSend}`,
            inputValue: '',
            buttonState: 'disabled'
          }));
          
          setTimeout(() => {
            handleSendMessage(inputToSend);
          }, 10);
        } else {
          console.log('Not sending - empty input or loading:', 
            'input:', currentValue, 'loading:', loading);
        }
      });
      
      const hasContent = newTextarea.value.trim().length > 0;
      newButton.disabled = loading || !hasContent;
      newButton.style.opacity = (loading || !hasContent) ? '0.5' : '1';
      newButton.style.cursor = (loading || !hasContent) ? 'not-allowed' : 'pointer';
    }
    
    return () => {
      const textarea = textareaRef.current;
      const sendButton = sendButtonRef.current;
      
      if (textarea) {
        console.log('Cleaning up textarea event listeners');
      }
      
      if (sendButton) {
        console.log('Cleaning up send button event listeners');
      }
    };
  }, [loading]); // Re-initialize when loading state changes

  const handleSendMessage = async (message) => {
    if (!message.trim() || loading) return;
    
    setLoading(true);
    console.log(`Sending message: ${message}`);
    
    const newUserMessage = {
      role: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setChatMessages(prev => [...prev, newUserMessage]);
    
    const safetyTimeout = setTimeout(() => {
      setLoading(false);
      console.error('Request timed out after 30 seconds');
      
      setChatMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: '抱歉，请求超时。请检查您的网络连接并重试。',
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    }, 30000);
    
    try {
      const response = await fetch(`${API_BASE_URL}/chat/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: message,
          session_id: sessionId
        }),
      });
      
      clearTimeout(safetyTimeout);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Chat response:', data);
        
        if (data.session_id && (!sessionId || sessionId !== data.session_id)) {
          setSessionId(data.session_id);
          console.log(`Session ID set to: ${data.session_id}`);
        }
        
        if (data.messages && data.messages.length > 0) {
          const newMessages = data.messages.filter(msg => 
            msg.role === 'assistant' && 
            !chatMessages.some(existingMsg => 
              existingMsg.role === msg.role && 
              existingMsg.content === msg.content
            )
          );
          
          if (newMessages.length > 0) {
            setChatMessages(prev => [...prev, ...newMessages]);
          }
        } else {
          const systemMessage = {
            role: 'assistant',
            content: '我已理解您的需求，并更新了期望模型。',
            timestamp: new Date().toLocaleTimeString()
          };
          
          setChatMessages(prev => [...prev, systemMessage]);
        }
        
        if (data.expectation_id) {
          setExpectationId(data.expectation_id);
          console.log(`Expectation ID set to: ${data.expectation_id}`);
          
          const systemMessage = {
            role: 'assistant',
            content: `期望模型已生成，ID: ${data.expectation_id}。您可以继续完善需求，或者开始生成代码。`,
            timestamp: new Date().toLocaleTimeString()
          };
          
          setChatMessages(prev => [...prev, systemMessage]);
        }
        
        if (data.requires_clarification === false && !data.expectation_id) {
          const systemMessage = {
            role: 'assistant',
            content: '需求澄清已完成。您可以继续完善需求，或者开始生成代码。',
            timestamp: new Date().toLocaleTimeString()
          };
          
          setChatMessages(prev => [...prev, systemMessage]);
        }
      } else {
        console.error('Error response:', response.status);
        
        const errorMessage = {
          role: 'assistant',
          content: '抱歉，处理您的请求时出现了问题。请稍后再试。',
          timestamp: new Date().toLocaleTimeString()
        };
        
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      clearTimeout(safetyTimeout);
      console.error('Error sending message:', error);
      
      const errorMessage = {
        role: 'assistant',
        content: '抱歉，发送消息时出现了错误。请检查您的网络连接并重试。',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      
      if (sendButtonRef.current) {
        const textarea = textareaRef.current;
        const hasContent = textarea && textarea.value.trim().length > 0;
        
        sendButtonRef.current.disabled = !hasContent;
        sendButtonRef.current.style.opacity = hasContent ? '1' : '0.5';
        sendButtonRef.current.style.cursor = hasContent ? 'pointer' : 'not-allowed';
        
        setDebugInfo(prev => ({
          ...prev,
          buttonState: hasContent ? 'enabled' : 'disabled'
        }));
      }
    }
  };

  const handleGenerateCode = async () => {
    if (!sessionId) {
      console.error('No session ID available');
      return;
    }
    
    setLoading(true);
    setGenerationStatus('starting');
    setGenerationProgress(0);
    
    const startMessage = {
      role: 'system',
      content: '开始生成代码...',
      timestamp: new Date().toLocaleTimeString()
    };
    
    setChatMessages(prev => [...prev, startMessage]);
    
    try {
      const response = await fetch(`${API_BASE_URL}/generate/code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Generation response:', data);
        
        if (data.generation_id) {
          setGenerationId(data.generation_id);
          setGenerationStatus('in_progress');
          
          const systemMessage = {
            role: 'system',
            content: `代码生成已开始，ID: ${data.generation_id}。请稍候...`,
            timestamp: new Date().toLocaleTimeString()
          };
          
          setChatMessages(prev => [...prev, systemMessage]);
          
          pollGenerationProgress(data.generation_id);
        } else {
          setGenerationStatus('failed');
          
          const errorMessage = {
            role: 'system',
            content: '代码生成请求失败，未返回生成ID。',
            timestamp: new Date().toLocaleTimeString()
          };
          
          setChatMessages(prev => [...prev, errorMessage]);
        }
      } else {
        console.error('Error response:', response.status);
        setGenerationStatus('failed');
        
        const errorMessage = {
          role: 'system',
          content: '代码生成请求失败。请稍后再试。',
          timestamp: new Date().toLocaleTimeString()
        };
        
        setChatMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error generating code:', error);
      setGenerationStatus('failed');
      
      const errorMessage = {
        role: 'system',
        content: '代码生成请求出错。请检查您的网络连接并重试。',
        timestamp: new Date().toLocaleTimeString()
      };
      
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const pollGenerationProgress = async (genId) => {
    if (!genId) return;
    
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/generate/progress/${genId}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Progress data:', data);
          
          setGenerationProgress(data.progress || 0);
          
          if (data.status === 'completed') {
            clearInterval(pollInterval);
            setGenerationStatus('completed');
            
            const completionMessage = {
              role: 'system',
              content: `代码生成已完成！您可以下载生成的代码。`,
              timestamp: new Date().toLocaleTimeString()
            };
            
            setChatMessages(prev => [...prev, completionMessage]);
          } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            setGenerationStatus('failed');
            
            const failureMessage = {
              role: 'system',
              content: `代码生成失败。请检查您的需求并重试。`,
              timestamp: new Date().toLocaleTimeString()
            };
            
            setChatMessages(prev => [...prev, failureMessage]);
          }
        } else {
          console.error('Error fetching progress:', response.status);
        }
      } catch (error) {
        console.error('Error polling progress:', error);
        
        const errorMessage = {
          role: 'system',
          content: '获取生成进度时出错。生成可能仍在进行中。',
          timestamp: new Date().toLocaleTimeString()
        };
        
        setChatMessages(prev => [...prev, errorMessage]);
      }
    }, 2000);
    
    setTimeout(() => {
      clearInterval(pollInterval);
      
      if (generationStatus === 'in_progress') {
        setGenerationStatus('unknown');
        
        const timeoutMessage = {
          role: 'system',
          content: '生成进度查询超时。生成可能仍在进行中，请稍后检查。',
          timestamp: new Date().toLocaleTimeString()
        };
        
        setChatMessages(prev => [...prev, timeoutMessage]);
      }
    }, 300000);
  };

  const handleDownloadCode = () => {
    if (!generationId) return;
    
    window.open(`${API_BASE_URL}/generate/download/${generationId}`, '_blank');
  };

  const handleDownloadExpectation = () => {
    if (!expectationId) return;
    
    window.open(`${API_BASE_URL}/expectation/download/${expectationId}`, '_blank');
  };

  const handleRestartConversation = () => {
    if (window.confirm('确定要重新开始对话吗？这将清除当前的对话历史。')) {
      setSessionId(null);
      setExpectationId(null);
      setGenerationId(null);
      setGenerationProgress(0);
      setGenerationStatus('idle');
      
      setChatMessages([
        {
          role: 'assistant',
          content: '欢迎使用Expeta 2.0! 我是您的需求分析助手。请告诉我您想要构建的系统或功能，我会帮您澄清需求并生成期望模型。',
          timestamp: new Date().toLocaleTimeString()
        }
      ]);
    }
  };

  const formatMarkdown = (text) => {
    if (!text) return '';
    
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br />');
    
    return formatted;
  };

  return (
    <div className="chat-requirements-container">
      <div className="chat-header">
        <h2>统一需求对话</h2>
        <div className="token-usage">
          <div className="token-info">
            <span>可用令牌: {tokenUsage.available.toLocaleString()}</span>
            <span>已用令牌: {tokenUsage.used.toLocaleString()}</span>
            <span>总令牌: {tokenUsage.total.toLocaleString()}</span>
          </div>
          <div className="token-progress">
            <div 
              className="token-progress-bar" 
              style={{ width: `${(tokenUsage.used / tokenUsage.total) * 100}%` }}
            ></div>
          </div>
        </div>
        <div className="session-info">
          {sessionId && <span>会话ID: {sessionId}</span>}
          {expectationId && <span>期望ID: {expectationId}</span>}
        </div>
        <div className="chat-actions">
          <button 
            className="action-button restart-button"
            onClick={handleRestartConversation}
            disabled={loading}
          >
            <span className="material-symbols-rounded">refresh</span>
            重新开始
          </button>
          {expectationId && (
            <button 
              className="action-button download-button"
              onClick={handleDownloadExpectation}
              disabled={loading}
            >
              <span className="material-symbols-rounded">download</span>
              下载期望模型
            </button>
          )}
          {expectationId && (
            <button 
              className="action-button generate-button"
              onClick={handleGenerateCode}
              disabled={loading || generationStatus === 'in_progress'}
            >
              <span className="material-symbols-rounded">code</span>
              生成代码
            </button>
          )}
          {generationId && generationStatus === 'completed' && (
            <button 
              className="action-button download-button"
              onClick={handleDownloadCode}
              disabled={loading}
            >
              <span className="material-symbols-rounded">download</span>
              下载代码
            </button>
          )}
        </div>
      </div>
      
      {generationStatus === 'in_progress' && (
        <div className="generation-progress">
          <div className="progress-label">
            代码生成进度: {generationProgress}%
          </div>
          <div className="progress-bar-container">
            <div 
              className="progress-bar" 
              style={{ width: `${generationProgress}%` }}
            ></div>
          </div>
        </div>
      )}
      
      <div className="chat-messages">
        {chatMessages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role}`}
          >
            <div 
              className="message-content"
              dangerouslySetInnerHTML={{ __html: formatMarkdown(message.content) }}
            ></div>
            <div className="message-timestamp">{message.timestamp}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-container">
        <div className="input-wrapper">
          <textarea 
            ref={textareaRef}
            name="user-message"
            id="user-message"
            placeholder="请描述您的需求..."
            disabled={loading}
            rows="2"
            style={{ resize: 'vertical', minHeight: '40px' }}
          />
          <button 
            ref={sendButtonRef}
            type="button"
            className="send-button"
            data-testid="send-button"
            style={{ 
              background: '#4a6cf7',
              color: 'white',
              border: 'none',
              padding: '0 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'opacity 0.2s'
            }}
          >
            <span className="material-symbols-rounded">send</span>
          </button>
        </div>
      </div>
      
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-info">
          <h3>调试信息</h3>
          <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default EnhancedChatRequirements;
