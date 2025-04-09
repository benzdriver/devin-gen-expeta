import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function SemanticMediator({ sessionId }) {
  const [mediatorData, setMediatorData] = useState({
    registeredSources: [],
    transformations: [],
    activeTransformations: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [selectedTransformation, setSelectedTransformation] = useState(null);
  
  useEffect(() => {
    if (!sessionId) return;
    
    const fetchMediatorData = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/semantic_mediator/status`, {
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setMediatorData(data);
          setError(null);
        } else {
          setError(`Failed to fetch data: ${response.statusText}`);
        }
      } catch (error) {
        console.error('Error fetching semantic mediator data:', error);
        setError('Failed to fetch semantic mediator data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchMediatorData();
  }, [sessionId]);
  
  const handlePromoteTransformation = async (transformationId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/semantic_mediator/promote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        },
        body: JSON.stringify({
          transformation_id: transformationId
        })
      });
      
      if (response.ok) {
        // Refresh mediator data after successful promotion
        const fetchResponse = await fetch(`${API_BASE_URL}/semantic_mediator/status`, {
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        });
        
        if (fetchResponse.ok) {
          const data = await fetchResponse.json();
          setMediatorData(data);
        }
      }
    } catch (error) {
      console.error('Error promoting transformation:', error);
    }
  };
  
  const handleViewTransformationDetails = (transformation) => {
    setSelectedTransformation(transformation);
  };
  
  // Display loading state
  if (loading && !mediatorData.registeredSources.length) {
    return (
      <div className="semantic-mediator-container">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>加载语义中介层数据...</p>
        </div>
      </div>
    );
  }
  
  // Display error state
  if (error && !mediatorData.registeredSources.length) {
    return (
      <div className="semantic-mediator-container">
        <div className="error-container">
          <div className="error-icon">
            <span className="material-symbols-rounded">error</span>
          </div>
          <p>{error}</p>
          <button className="primary-button" onClick={() => window.location.reload()}>
            重试
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="semantic-mediator-container">
      <div className="section-header">
        <h2>语义中介层</h2>
        <div className="section-actions">
          <button className="secondary-button" onClick={() => setSelectedTab('overview')}>
            <span className="material-symbols-rounded">dashboard</span>
            <span>概览</span>
          </button>
          <button className="secondary-button" onClick={() => setSelectedTab('sources')}>
            <span className="material-symbols-rounded">hub</span>
            <span>数据源</span>
          </button>
          <button className="secondary-button" onClick={() => setSelectedTab('transformations')}>
            <span className="material-symbols-rounded">swap_horiz</span>
            <span>转换</span>
          </button>
          <button className="secondary-button" onClick={() => setSelectedTab('active')}>
            <span className="material-symbols-rounded">autorenew</span>
            <span>活动</span>
          </button>
        </div>
      </div>
      
      {selectedTab === 'overview' && (
        <div className="semantic-mediator-overview">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">系统架构</h3>
            </div>
            <div className="card-content">
              <div className="architecture-diagram">
                <div className="module-node clarifier">
                  <div className="module-icon">
                    <span className="material-symbols-rounded">psychology</span>
                  </div>
                  <div className="module-label">澄清器</div>
                </div>
                <div className="connector right"></div>
                <div className="module-node generator">
                  <div className="module-icon">
                    <span className="material-symbols-rounded">code</span>
                  </div>
                  <div className="module-label">生成器</div>
                </div>
                <div className="connector right"></div>
                <div className="module-node validator">
                  <div className="module-icon">
                    <span className="material-symbols-rounded">verified</span>
                  </div>
                  <div className="module-label">验证器</div>
                </div>
                <div className="connector bottom"></div>
                <div className="module-node memory">
                  <div className="module-icon">
                    <span className="material-symbols-rounded">database</span>
                  </div>
                  <div className="module-label">记忆系统</div>
                </div>
                <div className="semantic-mediator-node">
                  <div className="module-icon">
                    <span className="material-symbols-rounded">swap_horiz</span>
                  </div>
                  <div className="module-label">语义中介层</div>
                </div>
              </div>
              <div className="explanation-text">
                <p>语义中介层是 Expeta 2.0 的核心创新，它使各个模块能够通过语义理解而非预定义接口进行交互。每个模块只需表达"需要什么"而非"如何获取"，中介层负责查找合适的数据源并执行必要的转换。</p>
                <p>随着系统使用，中介层会学习常见的转换模式，并将其优化为函数甚至独立服务，从而在保持灵活性的同时提高性能。</p>
              </div>
            </div>
          </div>
          
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-header">
                <h3 className="stat-title">注册数据源</h3>
                <div className="stat-icon blue">
                  <span className="material-symbols-rounded">hub</span>
                </div>
              </div>
              <div className="stat-value">{mediatorData.registeredSources.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-header">
                <h3 className="stat-title">转换路径</h3>
                <div className="stat-icon green">
                  <span className="material-symbols-rounded">swap_horiz</span>
                </div>
              </div>
              <div className="stat-value">{mediatorData.transformations.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-header">
                <h3 className="stat-title">活动转换</h3>
                <div className="stat-icon orange">
                  <span className="material-symbols-rounded">autorenew</span>
                </div>
              </div>
              <div className="stat-value">{mediatorData.activeTransformations.length}</div>
            </div>
          </div>
        </div>
      )}
      
      {selectedTab === 'sources' && (
        <div className="data-sources">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">注册数据源</h3>
              <div className="section-actions">
                <div className="search-container">
                  <input type="text" placeholder="搜索数据源..." className="search-input" />
                  <span className="material-symbols-rounded search-icon">search</span>
                </div>
              </div>
            </div>
            <div className="card-content">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>模块ID</th>
                    <th>能力</th>
                    <th>语义签名</th>
                    <th>注册时间</th>
                  </tr>
                </thead>
                <tbody>
                  {mediatorData.registeredSources.map((source, index) => (
                    <tr key={index}>
                      <td>{source.moduleId}</td>
                      <td>
                        <div className="capabilities-list">
                          {source.capabilities.map((capability, idx) => (
                            <span key={idx} className="capability-tag">{capability}</span>
                          ))}
                        </div>
                      </td>
                      <td className="semantic-signature">{source.semanticSignature}</td>
                      <td>{source.registrationTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
      
      {selectedTab === 'transformations' && (
        <div className="transformations">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">转换路径</h3>
              <div className="section-actions">
                <div className="search-container">
                  <input type="text" placeholder="搜索转换..." className="search-input" />
                  <span className="material-symbols-rounded search-icon">search</span>
                </div>
              </div>
            </div>
            <div className="card-content">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>源模块</th>
                    <th>目标模块</th>
                    <th>描述</th>
                    <th>使用次数</th>
                    <th>成功率</th>
                    <th>提升级别</th>
                    <th>最后使用</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {mediatorData.transformations.map((transform, index) => (
                    <tr key={index}>
                      <td>{transform.id}</td>
                      <td>{transform.source}</td>
                      <td>{transform.target}</td>
                      <td>{transform.description}</td>
                      <td>{transform.usageCount}</td>
                      <td>{(transform.successRate * 100).toFixed(1)}%</td>
                      <td>
                        <span className={`level-badge ${transform.promotionLevel}`}>
                          {transform.promotionLevel === 'function' ? '函数' : 
                           transform.promotionLevel === 'service' ? '服务' : '动态'}
                        </span>
                      </td>
                      <td>{transform.lastUsed}</td>
                      <td>
                        <div className="action-buttons">
                          <button 
                            className="icon-button" 
                            onClick={() => handleViewTransformationDetails(transform)}
                            title="查看详情"
                          >
                            <span className="material-symbols-rounded">visibility</span>
                          </button>
                          {transform.promotionLevel !== 'service' && (
                            <button 
                              className="icon-button" 
                              onClick={() => handlePromoteTransformation(transform.id)}
                              title="提升级别"
                            >
                              <span className="material-symbols-rounded">upgrade</span>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {selectedTransformation && (
            <div className="card transformation-details">
              <div className="card-header">
                <h3 className="card-title">转换详情: {selectedTransformation.id}</h3>
                <button 
                  className="close-button"
                  onClick={() => setSelectedTransformation(null)}
                >
                  <span className="material-symbols-rounded">close</span>
                </button>
              </div>
              <div className="card-content">
                <div className="details-grid">
                  <div className="detail-item">
                    <div className="detail-label">源模块</div>
                    <div className="detail-value">{selectedTransformation.source}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">目标模块</div>
                    <div className="detail-value">{selectedTransformation.target}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">描述</div>
                    <div className="detail-value">{selectedTransformation.description}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">使用次数</div>
                    <div className="detail-value">{selectedTransformation.usageCount}</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">成功率</div>
                    <div className="detail-value">{(selectedTransformation.successRate * 100).toFixed(1)}%</div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">提升级别</div>
                    <div className="detail-value">
                      <span className={`level-badge ${selectedTransformation.promotionLevel}`}>
                        {selectedTransformation.promotionLevel === 'function' ? '函数' : 
                         selectedTransformation.promotionLevel === 'service' ? '服务' : '动态'}
                      </span>
                    </div>
                  </div>
                  <div className="detail-item">
                    <div className="detail-label">最后使用</div>
                    <div className="detail-value">{selectedTransformation.lastUsed}</div>
                  </div>
                </div>
                
                <div className="transformation-metrics">
                  <h4>性能指标</h4>
                  <div className="metrics-chart placeholder">
                    <div className="chart-label">转换延迟趋势</div>
                    <div className="chart-placeholder">此处将显示转换性能图表</div>
                  </div>
                </div>
                
                <div className="transformation-code">
                  <h4>生成的代码</h4>
                  <div className="code-block">
                    <pre>
                      <code>
{`async function transform_${selectedTransformation.id.replace('-', '_')}(source_data) {
  // 自动生成的转换函数
  try {
    // 特定转换逻辑
    const result = await processSourceFormat(source_data);
    return {
      success: true,
      data: result
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}`}
                      </code>
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {selectedTab === 'active' && (
        <div className="active-transformations">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">活动转换</h3>
              <button className="secondary-button">
                <span className="material-symbols-rounded">refresh</span>
                <span>刷新</span>
              </button>
            </div>
            <div className="card-content">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>源模块</th>
                    <th>目标模块</th>
                    <th>意图</th>
                    <th>状态</th>
                    <th>开始时间</th>
                    <th>结束时间</th>
                  </tr>
                </thead>
                <tbody>
                  {mediatorData.activeTransformations.map((active, index) => (
                    <tr key={index}>
                      <td>{active.id}</td>
                      <td>{active.source}</td>
                      <td>{active.target}</td>
                      <td>{active.intent}</td>
                      <td>
                        <span className={`status-badge ${active.status}`}>
                          {active.status === 'completed' ? '已完成' : 
                           active.status === 'in_progress' ? '处理中' : '等待中'}
                        </span>
                      </td>
                      <td>{active.startTime}</td>
                      <td>{active.endTime || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">实时转换监控</h3>
            </div>
            <div className="card-content">
              <div className="monitor-container">
                <div className="monitor-placeholder">
                  <div className="module-flow">
                    {mediatorData.registeredSources.map((source, index) => (
                      <div key={index} className="module-item">
                        <div className="module-node">
                          <div className="module-icon">
                            <span className="material-symbols-rounded">
                              {source.moduleId === 'clarifier' ? 'psychology' :
                               source.moduleId === 'generator' ? 'code' :
                               source.moduleId === 'validator' ? 'verified' : 'database'}
                            </span>
                          </div>
                          <div className="module-name">{source.moduleId}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="transformation-flow">
                    {mediatorData.activeTransformations.map((active, index) => (
                      <div key={index} className={`flow-item ${active.status}`}>
                        <div className="flow-source">{active.source}</div>
                        <div className="flow-arrow">
                          <span className="material-symbols-rounded">
                            arrow_forward
                          </span>
                        </div>
                        <div className="flow-target">{active.target}</div>
                        <div className="flow-status">
                          {active.status === 'completed' ? '✓' : 
                           active.status === 'in_progress' ? '⟳' : '⌛'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SemanticMediator;