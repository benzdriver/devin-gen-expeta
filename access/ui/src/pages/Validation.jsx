import React, { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function Validation({ sessionId }) {
  const [validationResults, setValidationResults] = useState({
    semantic_match: 92,
    test_pass_rate: 93.3,
    overall_score: 85,
    details: [
      {
        title: '语义匹配验证',
        status: 'passed',
        details: '代码实现与期望模型的语义匹配度为92%，超过阈值80%。',
        time: '2分钟前',
        author: '系统'
      },
      {
        title: '功能测试验证',
        status: 'passed',
        details: '执行了15个测试用例，通过率为93.3%（14/15）。',
        time: '2分钟前',
        author: '系统'
      },
      {
        title: '安全性验证',
        status: 'failed',
        details: '密码哈希方法不符合安全标准，建议使用更强的加密算法。',
        time: '2分钟前',
        author: '系统'
      }
    ]
  });
  
  const handleValidateCode = async () => {
    if (!sessionId) return;
    
    try {
      // 实际实现中，这里会调用后端 API
      /*
      const response = await fetch(`${API_BASE_URL}/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        },
        body: JSON.stringify({
          expectation_id: 'user_management_system'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setValidationResults(data);
      }
      */
    } catch (error) {
      console.error('Error validating code:', error);
    }
  };
  
  const handleFilterResults = () => {
    // 实现筛选验证结果的逻辑
    console.log('Filter validation results');
  };

  return (
    <>
      <div className="section-header">
        <h2>验证结果</h2>
        <div className="section-actions">
          <button className="primary-button validate-button" onClick={handleValidateCode}>
            <span className="material-symbols-rounded">verified</span>
            <span>验证代码</span>
          </button>
        </div>
      </div>
      
      <div className="validation-container">
        <div className="validation-summary">
          <div className="validation-stat">
            <div className="validation-stat-value">{validationResults.semantic_match}%</div>
            <div className="validation-stat-label">语义匹配度</div>
          </div>
          <div className="validation-stat">
            <div className="validation-stat-value">{validationResults.test_pass_rate}%</div>
            <div className="validation-stat-label">测试通过率</div>
          </div>
          <div className="validation-stat">
            <div className="validation-stat-value">{validationResults.overall_score}%</div>
            <div className="validation-stat-label">总体验证分数</div>
          </div>
        </div>
        
        <div className="validation-results">
          <div className="section-header">
            <h3>验证详情</h3>
            <div className="section-actions">
              <button className="secondary-button" onClick={handleFilterResults}>
                <span className="material-symbols-rounded">filter_list</span>
                <span>筛选</span>
              </button>
            </div>
          </div>
          
          {validationResults.details.map((item, index) => (
            <div key={index} className="validation-item">
              <div className="validation-item-header">
                <div className="validation-item-title">{item.title}</div>
                <div className={`validation-item-status ${item.status}`}>
                  {item.status === 'passed' ? '通过' : '未通过'}
                </div>
              </div>
              <div className="validation-item-details">
                {item.details}
              </div>
              <div className="validation-item-meta">
                <span><span className="material-symbols-rounded">schedule</span>{item.time}</span>
                <span><span className="material-symbols-rounded">person</span>{item.author}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

export default Validation; 