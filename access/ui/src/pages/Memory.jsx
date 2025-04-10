import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../App';

function Memory({ sessionId }) {
  const [memories, setMemories] = useState([]);
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('expectation');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [memoryDetail, setMemoryDetail] = useState(null);
  
  // 在组件加载时获取记忆数据
  useEffect(() => {
    if (sessionId) {
      fetchMemories(selectedCategory);
    }
  }, [sessionId, selectedCategory]);
  
  // 获取记忆列表
  const fetchMemories = async (category) => {
    if (!sessionId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/expectations`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const expectationsArray = data.expectations || [];
        
        const memoryItems = expectationsArray.map(exp => ({
          id: exp.id,
          title: exp.title || exp.name || exp.id,
          preview: exp.description || 'No description available',
          date: exp.created_at || new Date().toISOString(),
          type: 'expectation'
        }));
        
        setMemories(memoryItems);
        if (memoryItems.length > 0) {
          setSelectedMemory(memoryItems[0]);
          fetchMemoryDetail(memoryItems[0].id);
        } else {
          setSelectedMemory(null);
          setMemoryDetail(null);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || '获取记忆数据失败');
      }
    } catch (error) {
      console.error('Error fetching memories:', error);
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  // 获取记忆详情
  const fetchMemoryDetail = async (memoryId) => {
    if (!sessionId || !memoryId) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/expectation/${memoryId}`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const detailData = {
          id: data.id,
          title: data.title || data.name || data.id,
          description: data.description || 'No description available',
          last_updated: data.updated_at || data.created_at || new Date().toISOString(),
          sub_expectations: data.sub_expectations || [],
          constraints: data.constraints || [],
          related_memories: []
        };
        setMemoryDetail(detailData);
      } else {
        console.error('Failed to fetch memory detail');
      }
    } catch (error) {
      console.error('Error fetching memory detail:', error);
    }
  };
  
  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    
    if (category === 'expectation') {
      fetchMemories('expectations');
    } else if (category === 'code') {
      fetchCodeGenerations();
    } else if (category === 'validation') {
      fetchValidations();
    } else if (category === 'clarification') {
      fetchClarifications();
    }
  };
  
  const fetchCodeGenerations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/expectations`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const expectationsArray = data.expectations || [];
        
        const generationsPromises = expectationsArray.map(async (exp) => {
          try {
            const genResponse = await fetch(`${API_BASE_URL}/memory/generations/${exp.id}`, {
              headers: {
                'Content-Type': 'application/json',
                'Session-ID': sessionId
              }
            });
            
            if (genResponse.ok) {
              const genData = await genResponse.json();
              return {
                id: exp.id,
                title: `Code for ${exp.title || exp.name || exp.id}`,
                preview: `Generated code with ${genData.files?.length || 0} files`,
                date: genData.created_at || new Date().toISOString(),
                type: 'code',
                generation: genData
              };
            }
            return null;
          } catch (error) {
            console.error(`Error fetching generation for ${exp.id}:`, error);
            return null;
          }
        });
        
        const generations = (await Promise.all(generationsPromises)).filter(Boolean);
        
        setMemories(generations);
        if (generations.length > 0) {
          setSelectedMemory(generations[0]);
          setMemoryDetail({
            ...generations[0],
            description: `Generated code for expectation ${generations[0].id}`,
            files: generations[0].generation?.files || []
          });
        } else {
          setSelectedMemory(null);
          setMemoryDetail(null);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || '获取代码生成数据失败');
      }
    } catch (error) {
      console.error('Error fetching code generations:', error);
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchValidations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/memory/expectations`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const expectationsArray = data.expectations || [];
        
        const validationsPromises = expectationsArray.map(async (exp) => {
          try {
            const valResponse = await fetch(`${API_BASE_URL}/memory/validations/${exp.id}`, {
              headers: {
                'Content-Type': 'application/json',
                'Session-ID': sessionId
              }
            });
            
            if (valResponse.ok) {
              const valData = await valResponse.json();
              return {
                id: exp.id,
                title: `Validation for ${exp.title || exp.name || exp.id}`,
                preview: `Validation ${valData.passed ? 'passed' : 'failed'}`,
                date: valData.created_at || new Date().toISOString(),
                type: 'validation',
                validation: valData
              };
            }
            return null;
          } catch (error) {
            console.error(`Error fetching validation for ${exp.id}:`, error);
            return null;
          }
        });
        
        const validations = (await Promise.all(validationsPromises)).filter(Boolean);
        
        setMemories(validations);
        if (validations.length > 0) {
          setSelectedMemory(validations[0]);
          setMemoryDetail({
            ...validations[0],
            description: `Validation results for expectation ${validations[0].id}`,
            passed: validations[0].validation?.passed,
            semantic_match: validations[0].validation?.semantic_match,
            test_results: validations[0].validation?.test_results
          });
        } else {
          setSelectedMemory(null);
          setMemoryDetail(null);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || '获取验证结果失败');
      }
    } catch (error) {
      console.error('Error fetching validations:', error);
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  const fetchClarifications = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/clarify/conversations`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const conversationsArray = data.conversations || [];
        
        const clarificationItems = conversationsArray.map(conv => ({
          id: conv.id,
          title: `Conversation ${conv.id}`,
          preview: `Stage: ${conv.stage}`,
          date: new Date().toISOString(),
          type: 'clarification',
          conversation: conv
        }));
        
        setMemories(clarificationItems);
        if (clarificationItems.length > 0) {
          setSelectedMemory(clarificationItems[0]);
          setMemoryDetail({
            ...clarificationItems[0],
            description: `Clarification conversation ${clarificationItems[0].id}`,
            messages: clarificationItems[0].conversation?.previous_messages || [],
            stage: clarificationItems[0].conversation?.stage,
            current_expectation: clarificationItems[0].conversation?.current_expectation
          });
        } else {
          setSelectedMemory(null);
          setMemoryDetail(null);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || '获取澄清对话失败');
      }
    } catch (error) {
      console.error('Error fetching clarifications:', error);
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  const handleMemoryClick = (memory) => {
    setSelectedMemory(memory);
    
    if (memory.type === 'expectation') {
      fetchMemoryDetail(memory.id);
    } else if (memory.type === 'code' && memory.generation) {
      setMemoryDetail({
        ...memory,
        description: `Generated code for expectation ${memory.id}`,
        files: memory.generation?.files || []
      });
    } else if (memory.type === 'validation' && memory.validation) {
      setMemoryDetail({
        ...memory,
        description: `Validation results for expectation ${memory.id}`,
        passed: memory.validation?.passed,
        semantic_match: memory.validation?.semantic_match,
        test_results: memory.validation?.test_results
      });
    } else if (memory.type === 'clarification' && memory.conversation) {
      setMemoryDetail({
        ...memory,
        description: `Clarification conversation ${memory.id}`,
        messages: memory.conversation?.previous_messages || [],
        stage: memory.conversation?.stage,
        current_expectation: memory.conversation?.current_expectation
      });
    } else {
      fetchMemoryDetail(memory.id);
    }
  };
  
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    // 实现搜索功能
    if (e.target.value.trim()) {
      const filteredMemories = memories.filter(memory => 
        memory.title.toLowerCase().includes(e.target.value.toLowerCase()) ||
        memory.preview.toLowerCase().includes(e.target.value.toLowerCase())
      );
      // 仅更新显示，不重新加载
      if (filteredMemories.length > 0) {
        setSelectedMemory(filteredMemories[0]);
        fetchMemoryDetail(filteredMemories[0].id);
      }
    } else {
      // 如果搜索词为空，重新加载所有内容
      fetchMemories(selectedCategory);
    }
  };
  
  const handleEditMemory = async () => {
    if (!selectedMemory) return;
    
    if (selectedMemory.type === 'expectation') {
      window.location.href = `/expectations?expectation_id=${selectedMemory.id}`;
    } else if (selectedMemory.type === 'code') {
      window.location.href = `/code-generation?expectation_id=${selectedMemory.id}`;
    } else if (selectedMemory.type === 'validation') {
      window.location.href = `/validation?expectation_id=${selectedMemory.id}`;
    } else if (selectedMemory.type === 'clarification') {
      window.location.href = `/requirements?conversation_id=${selectedMemory.id}`;
    }
  };
  
  const handleDeleteMemory = async () => {
    if (!selectedMemory || !sessionId) return;
    
    alert('删除功能尚未实现');
    
    const updatedMemories = memories.filter(memory => memory.id !== selectedMemory.id);
    setMemories(updatedMemories);
    
    if (updatedMemories.length > 0) {
      setSelectedMemory(updatedMemories[0]);
      fetchMemoryDetail(updatedMemories[0].id);
    } else {
      setSelectedMemory(null);
      setMemoryDetail(null);
    }
  };

  return (
    <div className="memory-container">
      <div className="memory-sidebar">
        <div className="memory-search">
          <input 
            type="text" 
            placeholder="搜索记忆..." 
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>
        
        <div className="memory-categories">
          <h3>分类</h3>
          <div 
            className={`memory-category ${selectedCategory === 'expectation' ? 'active' : ''}`}
            onClick={() => handleCategoryChange('expectation')}
          >
            <span className="material-symbols-rounded">description</span>
            <span>期望</span>
          </div>
          <div 
            className={`memory-category ${selectedCategory === 'code' ? 'active' : ''}`}
            onClick={() => handleCategoryChange('code')}
          >
            <span className="material-symbols-rounded">code</span>
            <span>代码生成</span>
          </div>
          <div 
            className={`memory-category ${selectedCategory === 'validation' ? 'active' : ''}`}
            onClick={() => handleCategoryChange('validation')}
          >
            <span className="material-symbols-rounded">verified</span>
            <span>验证结果</span>
          </div>
          <div 
            className={`memory-category ${selectedCategory === 'clarification' ? 'active' : ''}`}
            onClick={() => handleCategoryChange('clarification')}
          >
            <span className="material-symbols-rounded">psychology</span>
            <span>需求澄清</span>
          </div>
        </div>
        
        {loading ? (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>加载记忆数据...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <div className="error-icon">
              <span className="material-symbols-rounded">error</span>
            </div>
            <p>{error}</p>
            <button className="primary-button" onClick={() => fetchMemories(selectedCategory)}>
              重试
            </button>
          </div>
        ) : (
          <div className="memory-items">
            <h3>记忆项 ({memories.length})</h3>
            {memories.length === 0 ? (
              <div className="empty-state">
                <p>没有找到{
                  selectedCategory === 'expectation' ? '期望' : 
                  selectedCategory === 'code' ? '代码生成' :
                  selectedCategory === 'validation' ? '验证结果' : '需求澄清'
                }记忆</p>
              </div>
            ) : (
              memories.map((memory) => (
                <div 
                  key={memory.id} 
                  className={`memory-item ${selectedMemory && selectedMemory.id === memory.id ? 'active' : ''}`}
                  onClick={() => handleMemoryClick(memory)}
                >
                  <div className="memory-item-header">
                    <div className="memory-item-title">{memory.title}</div>
                    <div className="memory-item-date">{memory.date}</div>
                  </div>
                  <div className="memory-item-preview">{memory.preview}</div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
      
      {selectedMemory && memoryDetail ? (
        <div className="memory-content">
          <div className="memory-detail-header">
            <div className="memory-detail-title">{memoryDetail.title}</div>
            <div className="memory-detail-actions">
              <button className="secondary-button" onClick={handleEditMemory}>
                <span className="material-symbols-rounded">edit</span>
                <span>编辑</span>
              </button>
              <button className="secondary-button" onClick={handleDeleteMemory}>
                <span className="material-symbols-rounded">delete</span>
                <span>删除</span>
              </button>
            </div>
          </div>
          
          <div className="memory-detail-meta">
            <span><span className="material-symbols-rounded">calendar_today</span>创建于 {selectedMemory.date}</span>
            <span><span className="material-symbols-rounded">update</span>最后更新 {memoryDetail.last_updated || selectedMemory.date}</span>
            <span><span className="material-symbols-rounded">category</span>{
              selectedMemory.type === 'expectation' ? '期望' : 
              selectedMemory.type === 'code' ? '代码生成' :
              selectedMemory.type === 'validation' ? '验证结果' : '需求澄清'
            }</span>
          </div>
          
          <div className="memory-detail-content">
            <h3>{memoryDetail.title}</h3>
            <p>{memoryDetail.description}</p>
            
            {memoryDetail.sub_expectations && memoryDetail.sub_expectations.length > 0 && (
              <>
                <h4>子期望</h4>
                <ul>
                  {memoryDetail.sub_expectations.map((subExp, index) => (
                    <li key={index}><strong>{subExp.name || `子期望 ${index+1}`}</strong>：{subExp.description}</li>
                  ))}
                </ul>
              </>
            )}
            
            {memoryDetail.constraints && memoryDetail.constraints.length > 0 && (
              <>
                <h4>约束条件</h4>
                <ul>
                  {memoryDetail.constraints.map((constraint, index) => (
                    <li key={index}>{constraint.description || constraint}</li>
                  ))}
                </ul>
              </>
            )}
            
            {memoryDetail.related_memories && memoryDetail.related_memories.length > 0 && (
              <>
                <h4>相关记忆</h4>
                <ul>
                  {memoryDetail.related_memories.map((memory, index) => (
                    <li key={index}>
                      <a href="#" onClick={(e) => {
                        e.preventDefault();
                        // 根据ID查找并显示相关记忆
                        const relatedMemory = memories.find(m => m.id === memory.id);
                        if (relatedMemory) {
                          handleMemoryClick(relatedMemory);
                        }
                      }}>
                        {memory.title} ({memory.date})
                      </a>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </div>
      ) : !loading && (
        <div className="memory-content empty-state">
          <p>选择一个记忆项查看详细信息</p>
        </div>
      )}
    </div>
  );
}

export default Memory;                