import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../App';

function Expectations({ sessionId }) {
  const [expectations, setExpectations] = useState([]);
  const [selectedExpectation, setSelectedExpectation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [subExpectations, setSubExpectations] = useState([]);
  const [constraints, setConstraints] = useState([]);
  
  useEffect(() => {
    if (!sessionId) return;
    
    const fetchExpectations = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${API_BASE_URL}/memory/expectations`, {
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          const expectationsArray = data.expectations || [];
          setExpectations(expectationsArray);
          if (expectationsArray.length > 0) {
            // Select the first expectation automatically
            await fetchExpectationDetails(expectationsArray[0].id);
          } else {
            setLoading(false);
          }
        } else {
          const errorData = await response.json();
          setError(errorData.error || '获取期望列表失败');
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching expectations:', error);
        setError('网络错误，请重试');
        setLoading(false);
      }
    };
    
    fetchExpectations();
  }, [sessionId]);
  
  const fetchExpectationDetails = async (expectationId) => {
    if (!sessionId) return;
    
    try {
      setLoading(true);
      
      const expectationResponse = await fetch(`${API_BASE_URL}/memory/expectation/${expectationId}`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (expectationResponse.ok) {
        const expectationData = await expectationResponse.json();
        setSelectedExpectation(expectationData);
        
        // Fetch sub-expectations if available
        if (expectationData.sub_expectations_ids && expectationData.sub_expectations_ids.length > 0) {
          const subExpResponse = await fetch(
            `${API_BASE_URL}/memory/sub_expectations/${expectationId}`,
            {
              headers: {
                'Content-Type': 'application/json',
                'Session-ID': sessionId
              }
            }
          );
          
          if (subExpResponse.ok) {
            const subExpData = await subExpResponse.json();
            setSubExpectations(subExpData);
          }
        } else {
          setSubExpectations([]);
        }
        
        // Set constraints
        if (expectationData.constraints) {
          setConstraints(expectationData.constraints);
        } else {
          setConstraints([]);
        }
      } else {
        const errorData = await expectationResponse.json();
        throw new Error(errorData.error || '获取期望详情失败');
      }
    } catch (error) {
      console.error('Error fetching expectation details:', error);
      setError(error.message || '网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  const handleExpectationClick = async (expectation) => {
    await fetchExpectationDetails(expectation.id);
  };
  
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };
  
  const handleCreateExpectation = () => {
    // 导航到需求页面来创建新期望
    window.location.href = '/requirements';
  };
  
  const handleEditExpectation = async () => {
    if (!selectedExpectation || !sessionId) return;
    
    window.location.href = `/requirements?expectation_id=${selectedExpectation.id}`;
  };
  
  const handleGenerateCode = async () => {
    if (!selectedExpectation || !sessionId) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        },
        body: JSON.stringify({
          expectation_id: selectedExpectation.id
        })
      });
      
      if (response.ok) {
        window.location.href = `/code-generation?expectation_id=${selectedExpectation.id}`;
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || '代码生成失败');
      }
    } catch (error) {
      console.error('Error starting code generation:', error);
      setError(error.message || '网络错误，请重试');
    }
  };
  
  const filteredExpectations = expectations.filter(exp => {
    const matchesSearch = exp.title?.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         exp.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         exp.id?.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (selectedFilter === 'all') return matchesSearch;
    return matchesSearch && exp.status === selectedFilter;
  });

  if (loading && !selectedExpectation && expectations.length === 0) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>加载期望数据...</p>
      </div>
    );
  }

  if (error && !selectedExpectation && expectations.length === 0) {
    return (
      <div className="error-container">
        <div className="error-icon">
          <span className="material-symbols-rounded">error</span>
        </div>
        <p>{error}</p>
        <button className="primary-button" onClick={() => window.location.reload()}>
          重试
        </button>
      </div>
    );
  }

  return (
    <div className="expectations-container">
      <div className="expectation-list">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">期望列表</h3>
            <div className="search-container">
              <input 
                type="text" 
                placeholder="搜索期望..." 
                className="search-input"
                value={searchQuery}
                onChange={handleSearchChange}
              />
              <span className="material-symbols-rounded search-icon">search</span>
            </div>
          </div>
          <div className="card-content">
            {filteredExpectations.length > 0 ? (
              filteredExpectations.map(exp => (
                <div 
                  key={exp.id} 
                  className={`expectation-item ${selectedExpectation?.id === exp.id ? 'selected' : ''}`}
                  onClick={() => handleExpectationClick(exp)}
                >
                  <div className="expectation-header">
                    <span className="expectation-id">{exp.id}</span>
                    <span className={`expectation-status ${exp.status || 'active'}`}>
                      {exp.status === 'draft' ? '草稿' : '活跃'}
                    </span>
                  </div>
                  <h4 className="expectation-title">{exp.title || exp.name}</h4>
                  <p className="expectation-description">{exp.description}</p>
                </div>
              ))
            ) : (
              <div className="no-expectations">
                <p>没有找到期望。</p>
                <button className="primary-button" onClick={handleCreateExpectation}>
                  创建新期望
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {selectedExpectation && (
        <div className="expectation-detail">
          <div className="expectation-detail-header">
            <h3 className="expectation-detail-title">{selectedExpectation.title || selectedExpectation.name}</h3>
            <div className="expectation-detail-actions">
              <button className="secondary-button" onClick={handleEditExpectation}>
                <span className="material-symbols-rounded">edit</span>
                <span>编辑</span>
              </button>
              <button className="primary-button" onClick={handleGenerateCode}>
                <span className="material-symbols-rounded">code</span>
                <span>生成代码</span>
              </button>
            </div>
          </div>
          
          <div className="expectation-section">
            <h3>基本信息</h3>
            <div className="expectation-property">
              <div className="expectation-property-label">ID</div>
              <div className="expectation-property-value">{selectedExpectation.id}</div>
            </div>
            <div className="expectation-property">
              <div className="expectation-property-label">状态</div>
              <div className="expectation-property-value">
                {selectedExpectation.status === 'draft' ? '草稿' : '活跃'}
              </div>
            </div>
            {selectedExpectation.created_at && (
              <div className="expectation-property">
                <div className="expectation-property-label">创建时间</div>
                <div className="expectation-property-value">
                  {new Date(selectedExpectation.created_at).toLocaleString()}
                </div>
              </div>
            )}
            {selectedExpectation.updated_at && (
              <div className="expectation-property">
                <div className="expectation-property-label">最后更新</div>
                <div className="expectation-property-value">
                  {new Date(selectedExpectation.updated_at).toLocaleString()}
                </div>
              </div>
            )}
          </div>
          
          <div className="expectation-section">
            <h3>描述</h3>
            <div className="expectation-property">
              <div className="expectation-property-value">
                {selectedExpectation.description}
              </div>
            </div>
          </div>
          
          {subExpectations.length > 0 && (
            <div className="expectation-section">
              <h3>子期望</h3>
              {subExpectations.map((subExp, index) => (
                <div key={index} className="sub-expectation">
                  <p><strong>ID:</strong> {subExp.id}</p>
                  <p><strong>描述:</strong> {subExp.description}</p>
                  {subExp.criteria && subExp.criteria.length > 0 && (
                    <div>
                      <p><strong>验收标准:</strong></p>
                      <ul>
                        {subExp.criteria.map((criterion, idx) => (
                          <li key={idx}>{criterion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {constraints.length > 0 && (
            <div className="expectation-section">
              <h3>约束条件</h3>
              <ul className="constraints-list">
                {constraints.map((constraint, index) => (
                  <li key={index} className="constraint-item">{constraint}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Expectations;          