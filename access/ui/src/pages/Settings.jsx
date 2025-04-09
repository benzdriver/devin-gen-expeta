import React, { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function Settings({ userData, setUserData }) {
  const [settings, setSettings] = useState({
    profile: {
      name: userData.name,
      email: 'zhang.ming@example.com',
      role: userData.role
    },
    interface: {
      language: '简体中文',
      theme: '浅色',
      dashboardLayout: '标准'
    },
    ai: {
      primaryProvider: 'Anthropic',
      secondaryProvider: 'OpenAI',
      contextWindow: '8K',
      temperature: 0.7
    },
    notifications: {
      emailNotifications: true,
      desktopNotifications: false,
      notifyOnGeneration: true,
      notifyOnValidation: true
    },
    security: {
      sessionTimeout: 30,
      requireRevalidation: true,
      twoFactorAuth: false
    }
  });
  
  const [activeSection, setActiveSection] = useState('profile');
  const [isDirty, setIsDirty] = useState(false);
  
  const handleInputChange = (section, field, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
    setIsDirty(true);
  };
  
  const handleSaveChanges = async () => {
    if (!isDirty) return;
    
    // 更新用户显示名称
    if (settings.profile.name !== userData.name) {
      setUserData(prev => ({
        ...prev,
        name: settings.profile.name
      }));
    }
    
    try {
      // 实际实现中，这里会调用后端 API
      /*
      const response = await fetch(`${API_BASE_URL}/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });
      
      if (response.ok) {
        setIsDirty(false);
      }
      */
      
      // 仅用于演示
      console.log('Settings saved:', settings);
      setIsDirty(false);
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };
  
  const handleCancel = () => {
    // 重置为原始值
    setSettings({
      profile: {
        name: userData.name,
        email: 'zhang.ming@example.com',
        role: userData.role
      },
      interface: {
        language: '简体中文',
        theme: '浅色',
        dashboardLayout: '标准'
      },
      ai: {
        primaryProvider: 'Anthropic',
        secondaryProvider: 'OpenAI',
        contextWindow: '8K',
        temperature: 0.7
      },
      notifications: {
        emailNotifications: true,
        desktopNotifications: false,
        notifyOnGeneration: true,
        notifyOnValidation: true
      },
      security: {
        sessionTimeout: 30,
        requireRevalidation: true,
        twoFactorAuth: false
      }
    });
    setIsDirty(false);
  };

  return (
    <div className="settings-container">
      <div className="settings-sidebar">
        <div 
          className={`settings-category ${activeSection === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveSection('profile')}
        >
          <span className="material-symbols-rounded">account_circle</span>
          <span>个人资料</span>
        </div>
        <div 
          className={`settings-category ${activeSection === 'interface' ? 'active' : ''}`}
          onClick={() => setActiveSection('interface')}
        >
          <span className="material-symbols-rounded">tune</span>
          <span>系统设置</span>
        </div>
        <div 
          className={`settings-category ${activeSection === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveSection('ai')}
        >
          <span className="material-symbols-rounded">psychology</span>
          <span>AI设置</span>
        </div>
        <div 
          className={`settings-category ${activeSection === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveSection('notifications')}
        >
          <span className="material-symbols-rounded">notifications</span>
          <span>通知设置</span>
        </div>
        <div 
          className={`settings-category ${activeSection === 'security' ? 'active' : ''}`}
          onClick={() => setActiveSection('security')}
        >
          <span className="material-symbols-rounded">security</span>
          <span>安全设置</span>
        </div>
      </div>
      
      <div className="settings-content">
        {activeSection === 'profile' && (
          <div className="settings-section">
            <h3 className="settings-section-title">个人资料</h3>
            
            <div className="settings-item">
              <div className="settings-item-label">姓名</div>
              <div className="settings-item-description">您的显示名称</div>
              <div className="settings-item-control">
                <input 
                  type="text" 
                  value={settings.profile.name}
                  onChange={(e) => handleInputChange('profile', 'name', e.target.value)}
                />
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">电子邮件</div>
              <div className="settings-item-description">用于通知和账户恢复</div>
              <div className="settings-item-control">
                <input 
                  type="text" 
                  value={settings.profile.email}
                  onChange={(e) => handleInputChange('profile', 'email', e.target.value)}
                />
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">角色</div>
              <div className="settings-item-description">您在系统中的角色</div>
              <div className="settings-item-control">
                <select 
                  value={settings.profile.role}
                  onChange={(e) => handleInputChange('profile', 'role', e.target.value)}
                >
                  <option value="系统管理员">系统管理员</option>
                  <option value="开发者">开发者</option>
                  <option value="产品经理">产品经理</option>
                  <option value="普通用户">普通用户</option>
                </select>
              </div>
            </div>
          </div>
        )}
        
        {activeSection === 'interface' && (
          <div className="settings-section">
            <h3 className="settings-section-title">界面设置</h3>
            
            <div className="settings-item">
              <div className="settings-item-label">语言</div>
              <div className="settings-item-description">系统界面语言</div>
              <div className="settings-item-control">
                <select 
                  value={settings.interface.language}
                  onChange={(e) => handleInputChange('interface', 'language', e.target.value)}
                >
                  <option value="简体中文">简体中文</option>
                  <option value="English">English</option>
                  <option value="日本語">日本語</option>
                </select>
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">主题</div>
              <div className="settings-item-description">系统界面主题</div>
              <div className="settings-item-control">
                <select 
                  value={settings.interface.theme}
                  onChange={(e) => handleInputChange('interface', 'theme', e.target.value)}
                >
                  <option value="浅色">浅色</option>
                  <option value="深色">深色</option>
                  <option value="跟随系统">跟随系统</option>
                </select>
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">仪表盘布局</div>
              <div className="settings-item-description">仪表盘页面的默认布局</div>
              <div className="settings-item-control">
                <select 
                  value={settings.interface.dashboardLayout}
                  onChange={(e) => handleInputChange('interface', 'dashboardLayout', e.target.value)}
                >
                  <option value="标准">标准</option>
                  <option value="紧凑">紧凑</option>
                  <option value="宽松">宽松</option>
                </select>
              </div>
            </div>
          </div>
        )}
        
        {activeSection === 'ai' && (
          <div className="settings-section">
            <h3 className="settings-section-title">AI设置</h3>
            
            <div className="settings-item">
              <div className="settings-item-label">主要AI提供商</div>
              <div className="settings-item-description">首选的LLM提供商</div>
              <div className="settings-item-control">
                <select 
                  value={settings.ai.primaryProvider}
                  onChange={(e) => handleInputChange('ai', 'primaryProvider', e.target.value)}
                >
                  <option value="Anthropic">Anthropic (Claude)</option>
                  <option value="OpenAI">OpenAI (GPT)</option>
                  <option value="Google">Google (Gemini)</option>
                </select>
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">备选AI提供商</div>
              <div className="settings-item-description">当主要提供商不可用时使用</div>
              <div className="settings-item-control">
                <select 
                  value={settings.ai.secondaryProvider}
                  onChange={(e) => handleInputChange('ai', 'secondaryProvider', e.target.value)}
                >
                  <option value="OpenAI">OpenAI (GPT)</option>
                  <option value="Anthropic">Anthropic (Claude)</option>
                  <option value="Google">Google (Gemini)</option>
                  <option value="None">不设置备选</option>
                </select>
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">上下文窗口大小</div>
              <div className="settings-item-description">LLM处理的最大上下文长度</div>
              <div className="settings-item-control">
                <select 
                  value={settings.ai.contextWindow}
                  onChange={(e) => handleInputChange('ai', 'contextWindow', e.target.value)}
                >
                  <option value="4K">4K</option>
                  <option value="8K">8K</option>
                  <option value="16K">16K</option>
                  <option value="32K">32K</option>
                  <option value="100K">100K</option>
                </select>
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">温度</div>
              <div className="settings-item-description">控制生成文本的随机性（0.0-1.0）</div>
              <div className="settings-item-control">
                <input 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.1"
                  value={settings.ai.temperature}
                  onChange={(e) => handleInputChange('ai', 'temperature', parseFloat(e.target.value))}
                  style={{ width: '100%', maxWidth: '300px' }}
                />
                <span style={{ marginLeft: '10px' }}>{settings.ai.temperature}</span>
              </div>
            </div>
          </div>
        )}
        
        {activeSection === 'notifications' && (
          <div className="settings-section">
            <h3 className="settings-section-title">通知设置</h3>
            
            <div className="settings-item">
              <div className="settings-item-label">电子邮件通知</div>
              <div className="settings-item-description">接收电子邮件通知</div>
              <div className="settings-item-control">
                <input 
                  type="checkbox" 
                  checked={settings.notifications.emailNotifications}
                  onChange={(e) => handleInputChange('notifications', 'emailNotifications', e.target.checked)}
                />
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">桌面通知</div>
              <div className="settings-item-description">接收桌面推送通知</div>
              <div className="settings-item-control">
                <input 
                  type="checkbox" 
                  checked={settings.notifications.desktopNotifications}
                  onChange={(e) => handleInputChange('notifications', 'desktopNotifications', e.target.checked)}
                />
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">代码生成通知</div>
              <div className="settings-item-description">代码生成完成时通知</div>
              <div className="settings-item-control">
                <input 
                  type="checkbox" 
                  checked={settings.notifications.notifyOnGeneration}
                  onChange={(e) => handleInputChange('notifications', 'notifyOnGeneration', e.target.checked)}
                />
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">验证完成通知</div>
              <div className="settings-item-description">代码验证完成时通知</div>
              <div className="settings-item-control">
                <input 
                  type="checkbox" 
                  checked={settings.notifications.notifyOnValidation}
                  onChange={(e) => handleInputChange('notifications', 'notifyOnValidation', e.target.checked)}
                />
              </div>
            </div>
          </div>
        )}
        
        {activeSection === 'security' && (
          <div className="settings-section">
            <h3 className="settings-section-title">安全设置</h3>
            
            <div className="settings-item">
              <div className="settings-item-label">会话超时（分钟）</div>
              <div className="settings-item-description">无活动后会话超时时间</div>
              <div className="settings-item-control">
                <input 
                  type="number" 
                  min="5" 
                  max="120"
                  value={settings.security.sessionTimeout}
                  onChange={(e) => handleInputChange('security', 'sessionTimeout', parseInt(e.target.value))}
                />
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">敏感操作重新验证</div>
              <div className="settings-item-description">敏感操作时要求重新验证身份</div>
              <div className="settings-item-control">
                <input 
                  type="checkbox" 
                  checked={settings.security.requireRevalidation}
                  onChange={(e) => handleInputChange('security', 'requireRevalidation', e.target.checked)}
                />
              </div>
            </div>
            
            <div className="settings-item">
              <div className="settings-item-label">双因素认证</div>
              <div className="settings-item-description">启用双因素认证增强安全性</div>
              <div className="settings-item-control">
                <input 
                  type="checkbox" 
                  checked={settings.security.twoFactorAuth}
                  onChange={(e) => handleInputChange('security', 'twoFactorAuth', e.target.checked)}
                />
              </div>
            </div>
          </div>
        )}
        
        <div className="settings-actions">
          <button 
            className="secondary-button"
            onClick={handleCancel}
            disabled={!isDirty}
          >
            <span>取消</span>
          </button>
          <button 
            className="primary-button"
            onClick={handleSaveChanges}
            disabled={!isDirty}
          >
            <span>保存更改</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Settings; 