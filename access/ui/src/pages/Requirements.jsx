import React, { useState, useEffect, useRef } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function Requirements({ sessionId }) {
  const [activeStep, setActiveStep] = useState(1);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expectationData, setExpectationData] = useState({
    top_level_expectation: null,
    sub_expectations: [],
    constraints: []
  });
  const [confirmingRequirements, setConfirmingRequirements] = useState(false);
  
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, isTyping]);

  useEffect(() => {
    if (sessionId) {
      // 初始化聊天
      setChatMessages([{
        role: 'system',
        content: '欢迎使用Expeta 2.0! 我是您的需求分析助手。请告诉我您想要构建的系统或功能，我会帮您澄清需求并生成期望模型。',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
      
      // 检查是否有之前的对话
      fetchConversationHistory();
    }
  }, [sessionId]);
  
  // 获取对话历史
  const fetchConversationHistory = async () => {
    try {
      // 由于API不支持获取对话历史的端点，我们暂时不实现此功能
      // 在实际应用中，这里会调用API获取最近的对话
      console.log('获取对话历史功能暂未实现');
    } catch (error) {
      console.error('Error fetching conversation history:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !sessionId) return;
    
    const userMessage = {
      role: 'user',
      content: newMessage,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setChatMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsTyping(true);
    
    try {
      // 处理用户对确认请求的回应
      if (confirmingRequirements) {
        const confirmation = newMessage.toLowerCase();
        if (confirmation.includes('是') || confirmation.includes('确认') || confirmation.includes('yes') || confirmation.includes('确定')) {
          // 用户确认了需求，生成期望模型
          await handleGenerateExpectation();
          setConfirmingRequirements(false);
        } else {
          // 用户不确认，继续对话
          setConfirmingRequirements(false);
          const systemMessage = {
            role: 'system',
            content: '好的，让我们继续讨论您的需求。请告诉我您想要修改或添加的内容。',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          setChatMessages(prev => [...prev, systemMessage]);
        }
        setIsTyping(false);
        return;
      }

      // 正常消息处理
      // 使用/chat/session端点进行所有聊天操作
      const response = await fetch(`${API_BASE_URL}/chat/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        },
        body: JSON.stringify({
          user_message: userMessage.content,
          session_id: conversationId
        })
      });
      
      if (response.ok) {
        const data = await response.json();

        // 设置会话ID（如果是新会话）
        if (!conversationId && data.session_id) {
          setConversationId(data.session_id);
          setActiveStep(2); // 更新到澄清步骤
        }
        
        // 更新期望数据
        if (data.expectation) {
          setExpectationData(data.expectation);
        }
        
        // 添加系统回复
        const systemMessage = {
          role: 'system',
          content: data.response || '我已理解您的需求，并更新了期望模型。',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatMessages(prev => [...prev, systemMessage]);
        
        // 在几轮对话后询问用户是否确认需求
        const userMessagesCount = chatMessages.filter(msg => msg.role === 'user').length;
        if (userMessagesCount >= 2 && !confirmingRequirements) {
          setTimeout(() => {
            const confirmMessage = {
              role: 'system',
              content: '您对当前的需求澄清满意吗？如果满意，我可以为您生成正式的期望模型。',
              time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            };
            setChatMessages(prev => [...prev, confirmMessage]);
            setConfirmingRequirements(true);
          }, 1000);
        }
      } else {
        const errorData = await response.json();
        setChatMessages(prev => [...prev, {
          role: 'system',
          content: `错误: ${errorData.detail ? JSON.stringify(errorData.detail) : (errorData.error || '消息处理失败')}`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      setChatMessages(prev => [...prev, {
        role: 'system',
        content: '网络错误，请重试',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleGenerateExpectation = async () => {
    if (!sessionId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // 使用/process端点生成期望模型
      const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        },
        body: JSON.stringify({
          text: chatMessages
            .filter(msg => msg.role === 'user')
            .map(msg => msg.content)
            .join("\n")
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.clarification) {
          setExpectationData(data.clarification);
          setActiveStep(3);
          
          // 添加系统消息
          setChatMessages(prev => [...prev, {
            role: 'system',
            content: '期望模型已完成并存储。您可以在右侧查看详细的期望清单。需要继续完善吗？',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]);
        } else {
          setError('生成期望模型时出错：未返回期望数据');
          
          setChatMessages(prev => [...prev, {
            role: 'system',
            content: '生成期望模型失败：未返回期望数据',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail ? JSON.stringify(errorData.detail) : (errorData.error || '期望生成过程中出现问题'));
        
        setChatMessages(prev => [...prev, {
          role: 'system',
          content: `生成期望模型失败: ${errorData.detail ? JSON.stringify(errorData.detail) : (errorData.error || '未知错误')}`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }]);
      }
    } catch (error) {
      console.error('Error finalizing expectation:', error);
      setError('网络错误，请重试');
      
      setChatMessages(prev => [...prev, {
        role: 'system',
        content: '网络错误，生成期望模型失败。请重试。',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleRestartConversation = () => {
    if (window.confirm('确定要重新开始对话吗？当前的对话内容将不会保存。')) {
      setConversationId(null);
      setActiveStep(1);
      setExpectationData({
        top_level_expectation: null,
        sub_expectations: [],
        constraints: []
      });
      setChatMessages([{
        role: 'system',
        content: '让我们重新开始。请告诉我您想要构建的系统或功能。',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
      setConfirmingRequirements(false);
    }
  };

  return (
    <>
      {/* 工作流程可视化 */}
      <section className="workflow-section">
        <div className="section-header">
          <h2>处理流程</h2>
          <div className="section-actions">
            <button 
              className="secondary-button" 
              onClick={handleRestartConversation}
              title="重新开始对话"
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
              <button 
                className="primary-button" 
                onClick={handleGenerateExpectation}
                disabled={!conversationId || loading}
              >
                <span className="material-symbols-rounded">check_circle</span>
                <span>确认并生成期望</span>
              </button>
            </div>
          </div>
          <div className="chat-container">
            <div className="chat-messages">
              {chatMessages.map((message, index) => (
                <div 
                  key={index} 
                  className={`message ${message.role === 'user' ? 'user-message' : 'system-message'}`}
                >
                  <div className="message-content">
                    <p>{message.content}</p>
                  </div>
                  <div className="message-time">{message.time}</div>
                </div>
              ))}
              {isTyping && (
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="chat-input">
              <textarea 
                placeholder="请描述您的需求..."
                rows="1"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
              />
              <button 
                className={`send-button ${loading ? 'disabled' : ''}`} 
                onClick={handleSendMessage}
                disabled={loading}
              >
                <span className="material-symbols-rounded">send</span>
              </button>
            </div>
          </div>
        </section>

        {/* 期望展示区域 */}
        <section className="expectation-display-section">
          <div className="section-header">
            <h2>期望模型</h2>
            <div className="section-actions">
              {activeStep >= 3 && (
                <button className="secondary-button">
                  <span className="material-symbols-rounded">download</span>
                  <span>导出</span>
                </button>
              )}
            </div>
          </div>
          <div className="expectation-display">
            {!expectationData.top_level_expectation ? (
              <div className="empty-state">
                <span className="material-symbols-rounded large-icon">format_list_bulleted</span>
                <p>期望模型将在对话过程中生成</p>
                <p className="secondary-text">请在左侧开始描述您的需求</p>
              </div>
            ) : (
              <div className="expectation-content">
                <div className="expectation-card main-expectation">
                  <div className="card-header">
                    <h3>主要期望</h3>
                  </div>
                  <div className="card-content">
                    <p className="expectation-id">ID: {expectationData.top_level_expectation.id}</p>
                    <p className="expectation-description">{expectationData.top_level_expectation.description}</p>
                  </div>
                </div>
                
                {expectationData.sub_expectations.length > 0 && (
                  <div className="expectation-card sub-expectations">
                    <div className="card-header">
                      <h3>子期望</h3>
                      <span className="count-badge">{expectationData.sub_expectations.length}</span>
                    </div>
                    <div className="card-content">
                      {expectationData.sub_expectations.map((subExp, index) => (
                        <div key={index} className="sub-expectation-item">
                          <div className="item-header">
                            <span className="item-number">{index + 1}</span>
                            <span className="item-id">{subExp.id}</span>
                          </div>
                          <p className="item-description">{subExp.description}</p>
                          {subExp.criteria && subExp.criteria.length > 0 && (
                            <div className="criteria-list">
                              <h4>验收标准:</h4>
                              <ul>
                                {subExp.criteria.map((criteria, idx) => (
                                  <li key={idx}>{criteria}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {expectationData.constraints && expectationData.constraints.length > 0 && (
                  <div className="expectation-card constraints">
                    <div className="card-header">
                      <h3>约束条件</h3>
                      <span className="count-badge">{expectationData.constraints.length}</span>
                    </div>
                    <div className="card-content">
                      <ul className="constraints-list">
                        {expectationData.constraints.map((constraint, index) => (
                          <li key={index}>{constraint}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </div>
    </>
  );
}

export default Requirements; 