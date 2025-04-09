import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

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
      const response = await fetch(`${API_BASE_URL}/memory/${category}`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMemories(data.items || []);
        if (data.items && data.items.length > 0) {
          setSelectedMemory(data.items[0]);
          fetchMemoryDetail(data.items[0].id);
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
      const response = await fetch(`${API_BASE_URL}/memory/detail/${memoryId}`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMemoryDetail(data);
      } else {
        console.error('Failed to fetch memory detail');
      }
    } catch (error) {
      console.error('Error fetching memory detail:', error);
    }
  };
  
  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    fetchMemories(category);
  };
  
  const handleMemoryClick = (memory) => {
    setSelectedMemory(memory);
    fetchMemoryDetail(memory.id);
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
    
    console.log('Edit memory:', selectedMemory.id);
    // 实际编辑功能将在这里实现
    // 在实际应用中，这里会跳转到编辑页面或打开编辑对话框
  };
  
  const handleDeleteMemory = async () => {
    if (!selectedMemory || !sessionId) return;
    
    if (window.confirm(`确定要删除"${selectedMemory.title}"吗？`)) {
      try {
        const response = await fetch(`${API_BASE_URL}/memory/${selectedMemory.id}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        });
        
        if (response.ok) {
          // 从列表中移除已删除的记忆
          const updatedMemories = memories.filter(memory => memory.id !== selectedMemory.id);
          setMemories(updatedMemories);
          
          // 选择新的记忆项（如果有）
          if (updatedMemories.length > 0) {
            setSelectedMemory(updatedMemories[0]);
            fetchMemoryDetail(updatedMemories[0].id);
          } else {
            setSelectedMemory(null);
            setMemoryDetail(null);
          }
        } else {
          const errorData = await response.json();
          alert(errorData.error || '删除失败');
        }
      } catch (error) {
        console.error('Error deleting memory:', error);
        alert('删除过程中发生错误');
      }
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