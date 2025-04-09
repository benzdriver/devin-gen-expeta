import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function CodeGeneration({ sessionId }) {
  const [expectation, setExpectation] = useState(null);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [genOptions, setGenOptions] = useState({
    language: 'python',
    framework: 'flask',
    includeTests: true,
    includeDocumentation: true
  });
  const [expectationId, setExpectationId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeFile, setActiveFile] = useState(null);
  
  const handleInputChange = (e) => {
    setExpectationId(e.target.value);
  };
  
  const handleLoadExpectation = async () => {
    if (!sessionId || !expectationId.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/memory/expectation/${expectationId}`, {
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setExpectation(data);
      } else {
        const errorData = await response.json();
        setError(errorData.error || '期望数据加载失败');
      }
    } catch (error) {
      console.error('Error loading expectation:', error);
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };
  
  const handleOptionChange = (key, value) => {
    setGenOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };
  
  const handleGenerateCode = async () => {
    if (!sessionId || !expectation) return;
    
    setIsGenerating(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Session-ID': sessionId
        },
        body: JSON.stringify({
          expectation_id: expectation.id,
          options: genOptions
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setGeneratedCode(data);
        if (data && data.files && data.files.length > 0) {
          setActiveFile(data.files[0]);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || '代码生成失败');
      }
    } catch (error) {
      console.error('Error generating code:', error);
      setError('网络错误，请重试');
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleCopyCode = (content) => {
    navigator.clipboard.writeText(content)
      .then(() => {
        // 可以添加复制成功的提示
        console.log('Code copied to clipboard');
      })
      .catch(err => {
        console.error('Failed to copy code:', err);
      });
  };
  
  const handleDownloadFile = (file) => {
    const blob = new Blob([file.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name || file.path.split('/').pop();
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const handleDownloadAll = () => {
    if (!generatedCode || !generatedCode.files || generatedCode.files.length === 0) return;
    
    // 在实际场景中，可能需要使用jszip等库来创建zip文件
    // 这里仅作简单示例
    generatedCode.files.forEach(file => {
      handleDownloadFile(file);
    });
  };
  
  useEffect(() => {
    // If URL contains expectation_id parameter, load it automatically
    const queryParams = new URLSearchParams(window.location.search);
    const expId = queryParams.get('expectation_id');
    if (expId && sessionId) {
      setExpectationId(expId);
      
      // Fetch expectation data
      const fetchExpectation = async () => {
        try {
          setLoading(true);
          
          const response = await fetch(`${API_BASE_URL}/memory/expectation/${expId}`, {
            headers: {
              'Content-Type': 'application/json',
              'Session-ID': sessionId
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            setExpectation(data);
            
            // Check if code was already generated for this expectation
            const codeResponse = await fetch(`${API_BASE_URL}/memory/generations/${expId}`, {
              headers: {
                'Content-Type': 'application/json',
                'Session-ID': sessionId
              }
            });
            
            if (codeResponse.ok) {
              const codeData = await codeResponse.json();
              if (codeData && codeData.generated_code) {
                setGeneratedCode(codeData.generated_code);
                if (codeData.generated_code.files && codeData.generated_code.files.length > 0) {
                  setActiveFile(codeData.generated_code.files[0]);
                }
              }
            }
          }
        } catch (error) {
          console.error('Error loading expectation from URL parameter:', error);
        } finally {
          setLoading(false);
        }
      };
      
      fetchExpectation();
    }
  }, [sessionId]);
  
  return (
    <div className="code-generation-container">
      <div className="expectation-section">
        <div className="section-header">
          <h2>期望数据</h2>
          <div className="section-actions">
            <div className="search-container">
              <input 
                type="text" 
                placeholder="输入期望ID..." 
                className="search-input"
                value={expectationId}
                onChange={handleInputChange}
              />
              <button 
                className="primary-button" 
                onClick={handleLoadExpectation}
                disabled={loading || !expectationId.trim()}
              >
                加载
              </button>
            </div>
          </div>
        </div>
        
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>正在加载期望数据...</p>
          </div>
        )}
        
        {error && (
          <div className="error-container">
            <div className="error-icon">
              <span className="material-symbols-rounded">error</span>
            </div>
            <p>{error}</p>
            <button className="primary-button" onClick={() => setError(null)}>
              清除
            </button>
          </div>
        )}
        
        {expectation && (
          <div className="expectation-card">
            <div className="expectation-header">
              <h3>{expectation.title || expectation.name}</h3>
              <span className="expectation-id">{expectation.id}</span>
            </div>
            <div className="expectation-body">
              <p>{expectation.description}</p>
              
              {expectation.sub_expectations && expectation.sub_expectations.length > 0 && (
                <div className="expectation-sub-section">
                  <h4>子期望</h4>
                  <ul>
                    {expectation.sub_expectations.map((subExp, index) => (
                      <li key={index}>{subExp.name || subExp.description}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {expectation.constraints && expectation.constraints.length > 0 && (
                <div className="expectation-sub-section">
                  <h4>约束条件</h4>
                  <ul>
                    {expectation.constraints.map((constraint, index) => (
                      <li key={index}>{constraint}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}
        
        {expectation && (
          <div className="generation-options">
            <h3>生成选项</h3>
            <div className="options-grid">
              <div className="option-item">
                <label>编程语言</label>
                <select 
                  value={genOptions.language}
                  onChange={(e) => handleOptionChange('language', e.target.value)}
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="java">Java</option>
                  <option value="go">Go</option>
                </select>
              </div>
              
              <div className="option-item">
                <label>框架</label>
                <select 
                  value={genOptions.framework}
                  onChange={(e) => handleOptionChange('framework', e.target.value)}
                >
                  <option value="flask">Flask</option>
                  <option value="django">Django</option>
                  <option value="express">Express.js</option>
                  <option value="react">React</option>
                  <option value="spring">Spring</option>
                </select>
              </div>
              
              <div className="option-item checkbox">
                <label>
                  <input 
                    type="checkbox" 
                    checked={genOptions.includeTests}
                    onChange={(e) => handleOptionChange('includeTests', e.target.checked)}
                  />
                  包含测试
                </label>
              </div>
              
              <div className="option-item checkbox">
                <label>
                  <input 
                    type="checkbox" 
                    checked={genOptions.includeDocumentation}
                    onChange={(e) => handleOptionChange('includeDocumentation', e.target.checked)}
                  />
                  包含文档
                </label>
              </div>
            </div>
            
            <div className="generation-actions">
              <button 
                className="primary-button" 
                onClick={handleGenerateCode}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <span className="loading-spinner small"></span>
                    <span>正在生成...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-rounded">code</span>
                    <span>生成代码</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
      
      {generatedCode && (
        <div className="generated-code-section">
          <div className="section-header">
            <h2>生成的代码</h2>
            <div className="section-actions">
              <button className="secondary-button" onClick={handleDownloadAll}>
                <span className="material-symbols-rounded">download</span>
                <span>下载所有文件</span>
              </button>
            </div>
          </div>
          
          <div className="code-viewer">
            <div className="file-list">
              {generatedCode.files.map((file, index) => (
                <div 
                  key={index} 
                  className={`file-item ${activeFile && activeFile.path === file.path ? 'active' : ''}`}
                  onClick={() => setActiveFile(file)}
                >
                  <span className="material-symbols-rounded">description</span>
                  <span className="file-name">{file.name || file.path.split('/').pop()}</span>
                </div>
              ))}
            </div>
            
            <div className="code-content">
              {activeFile && (
                <>
                  <div className="code-header">
                    <div className="code-path">{activeFile.path}</div>
                    <div className="code-actions">
                      <button 
                        className="icon-button" 
                        onClick={() => handleCopyCode(activeFile.content)}
                        title="复制代码"
                      >
                        <span className="material-symbols-rounded">content_copy</span>
                      </button>
                      <button 
                        className="icon-button" 
                        onClick={() => handleDownloadFile(activeFile)}
                        title="下载文件"
                      >
                        <span className="material-symbols-rounded">download</span>
                      </button>
                    </div>
                  </div>
                  <pre className="code-block">
                    <code>{activeFile.content}</code>
                  </pre>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CodeGeneration; 