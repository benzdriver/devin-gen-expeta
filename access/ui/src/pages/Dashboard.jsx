import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../App';

function Dashboard({ sessionId }) {
  const [stats, setStats] = useState({
    requirements: { value: 24, change: 12 },
    expectations: { value: 42, change: 8 },
    generations: { value: 36, change: 15 },
    validations: { value: 87, change: 5 }
  });
  const [tokenStats, setTokenStats] = useState({
    total_tokens: 0,
    used_tokens: 0,
    available_tokens: 0,
    memory_usage: {
      expectations: 0,
      code: 0,
      conversations: 0,
      other: 0
    }
  });
  const [activities, setActivities] = useState([
    {
      id: 1,
      type: 'requirement',
      icon: 'description',
      title: '新需求已添加：用户管理系统',
      time: '今天 10:30'
    },
    {
      id: 2,
      type: 'expectation',
      icon: 'format_list_bulleted',
      title: '期望模型已生成：用户认证模块',
      time: '今天 09:45'
    },
    {
      id: 3,
      type: 'generation',
      icon: 'code',
      title: '代码已生成：数据验证工具类',
      time: '昨天 16:20'
    },
    {
      id: 4,
      type: 'validation',
      icon: 'verified',
      title: '验证完成：API接口模块',
      time: '昨天 14:15'
    },
    {
      id: 5,
      type: 'clarification',
      icon: 'psychology',
      title: '需求澄清完成：支付处理系统',
      time: '昨天 11:30'
    }
  ]);
  const [projects, setProjects] = useState([
    {
      id: 1,
      title: '电子商务平台后端API',
      description: '开发支持产品管理、用户账户和订单处理的RESTful API',
      status: 'in-progress',
      deadline: '2025-05-15',
      completion: 65
    },
    {
      id: 2,
      title: '用户管理系统',
      description: '实现用户注册、认证和个人资料管理功能',
      status: 'in-progress',
      deadline: '2025-04-30',
      completion: 40
    },
    {
      id: 3,
      title: '数据分析仪表板',
      description: '创建可视化仪表板，展示关键业务指标和趋势',
      status: 'new',
      deadline: '2025-06-10',
      completion: 10
    }
  ]);

  useEffect(() => {
    // 在实际实现中，这里会从后端获取仪表盘数据
    const fetchDashboardData = async () => {
      try {
        const statsResponse = await fetch(`${API_BASE_URL}/dashboard/stats`, {
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        }).catch(() => null);
        
        if (statsResponse && statsResponse.ok) {
          const data = await statsResponse.json();
          setStats(data.stats || stats);
          setActivities(data.activities || activities);
          setProjects(data.projects || projects);
        }
        
        const tokenResponse = await fetch(`${API_BASE_URL}/token/usage`, {
          headers: {
            'Content-Type': 'application/json',
            'Session-ID': sessionId
          }
        }).catch(() => null);
        
        if (tokenResponse && tokenResponse.ok) {
          const tokenData = await tokenResponse.json();
          setTokenStats(tokenData);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    if (sessionId) {
      fetchDashboardData();
      
      const tokenRefreshInterval = setInterval(async () => {
        try {
          const tokenResponse = await fetch(`${API_BASE_URL}/token/usage`, {
            headers: {
              'Content-Type': 'application/json',
              'Session-ID': sessionId
            }
          }).catch(() => null);
          
          if (tokenResponse && tokenResponse.ok) {
            const tokenData = await tokenResponse.json();
            setTokenStats(tokenData);
          }
        } catch (error) {
          console.error('Error refreshing token data:', error);
        }
      }, 60000);
      
      return () => clearInterval(tokenRefreshInterval);
    }
  }, [sessionId]);

  return (
    <>
      {/* 统计卡片 */}
      <div className="dashboard-grid">
        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">总需求数</h3>
            <div className="stat-icon blue">
              <span className="material-symbols-rounded">description</span>
            </div>
          </div>
          <div className="stat-value">{stats.requirements.value}</div>
          <div className="stat-description">较上月增长 {stats.requirements.change}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">期望模型数</h3>
            <div className="stat-icon green">
              <span className="material-symbols-rounded">format_list_bulleted</span>
            </div>
          </div>
          <div className="stat-value">{stats.expectations.value}</div>
          <div className="stat-description">较上月增长 {stats.expectations.change}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">代码生成数</h3>
            <div className="stat-icon orange">
              <span className="material-symbols-rounded">code</span>
            </div>
          </div>
          <div className="stat-value">{stats.generations.value}</div>
          <div className="stat-description">较上月增长 {stats.generations.change}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-header">
            <h3 className="stat-title">验证通过率</h3>
            <div className="stat-icon red">
              <span className="material-symbols-rounded">verified</span>
            </div>
          </div>
          <div className="stat-value">{stats.validations.value}%</div>
          <div className="stat-description">较上月提升 {stats.validations.change}%</div>
        </div>
      </div>
      
      {/* Token使用统计 */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Token使用统计</h3>
          <button 
            className="secondary-button"
            onClick={() => {
              if (sessionId) {
                fetch(`${API_BASE_URL}/token/usage`, {
                  headers: {
                    'Content-Type': 'application/json',
                    'Session-ID': sessionId
                  }
                })
                .then(response => response.ok ? response.json() : null)
                .then(data => data ? setTokenStats(data) : null)
                .catch(error => console.error('Error refreshing token data:', error));
              }
            }}
          >
            <span className="material-symbols-rounded">refresh</span>
            <span>刷新</span>
          </button>
        </div>
        <div className="card-content">
          <div className="token-stats">
            <div className="token-usage-bar">
              <div 
                className="token-used" 
                style={{ 
                  width: `${tokenStats.total_tokens > 0 ? (tokenStats.used_tokens / tokenStats.total_tokens) * 100 : 0}%` 
                }}
              ></div>
            </div>
            <div className="token-stats-details">
              <div className="token-stat">
                <span className="token-label">总Token数:</span>
                <span className="token-value">{tokenStats.total_tokens.toLocaleString()}</span>
              </div>
              <div className="token-stat">
                <span className="token-label">已使用:</span>
                <span className="token-value">{tokenStats.used_tokens.toLocaleString()}</span>
              </div>
              <div className="token-stat">
                <span className="token-label">可用:</span>
                <span className="token-value">{tokenStats.available_tokens.toLocaleString()}</span>
              </div>
            </div>
          </div>
          
          <h4 className="memory-usage-title">记忆使用分布</h4>
          <div className="memory-usage">
            <div className="memory-item">
              <div className="memory-label">期望模型</div>
              <div className="memory-bar-container">
                <div 
                  className="memory-bar expectations" 
                  style={{ 
                    width: `${tokenStats.used_tokens > 0 ? (tokenStats.memory_usage.expectations / tokenStats.used_tokens) * 100 : 0}%` 
                  }}
                ></div>
              </div>
              <div className="memory-value">{tokenStats.memory_usage.expectations.toLocaleString()}</div>
            </div>
            <div className="memory-item">
              <div className="memory-label">代码生成</div>
              <div className="memory-bar-container">
                <div 
                  className="memory-bar code" 
                  style={{ 
                    width: `${tokenStats.used_tokens > 0 ? (tokenStats.memory_usage.code / tokenStats.used_tokens) * 100 : 0}%` 
                  }}
                ></div>
              </div>
              <div className="memory-value">{tokenStats.memory_usage.code.toLocaleString()}</div>
            </div>
            <div className="memory-item">
              <div className="memory-label">对话记录</div>
              <div className="memory-bar-container">
                <div 
                  className="memory-bar conversations" 
                  style={{ 
                    width: `${tokenStats.used_tokens > 0 ? (tokenStats.memory_usage.conversations / tokenStats.used_tokens) * 100 : 0}%` 
                  }}
                ></div>
              </div>
              <div className="memory-value">{tokenStats.memory_usage.conversations.toLocaleString()}</div>
            </div>
            <div className="memory-item">
              <div className="memory-label">其他</div>
              <div className="memory-bar-container">
                <div 
                  className="memory-bar other" 
                  style={{ 
                    width: `${tokenStats.used_tokens > 0 ? (tokenStats.memory_usage.other / tokenStats.used_tokens) * 100 : 0}%` 
                  }}
                ></div>
              </div>
              <div className="memory-value">{tokenStats.memory_usage.other.toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>

      {/* 最近活动 */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">最近活动</h3>
          <button className="secondary-button">
            <span className="material-symbols-rounded">refresh</span>
            <span>刷新</span>
          </button>
        </div>
        <div className="card-content">
          <div className="activity-list">
            {activities.map(activity => {
              const getIconClass = () => {
                switch (activity.type) {
                  case 'requirement': return 'blue';
                  case 'expectation': return 'green';
                  case 'generation': return 'orange';
                  case 'validation': return 'blue';
                  case 'clarification': return 'green';
                  default: return 'blue';
                }
              };

              return (
                <div key={activity.id} className="activity-item">
                  <div className={`activity-icon ${getIconClass()}`}>
                    <span className="material-symbols-rounded">{activity.icon}</span>
                  </div>
                  <div className="activity-content">
                    <div className="activity-title">{activity.title}</div>
                    <div className="activity-time">{activity.time}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* 进行中的项目 */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">进行中的项目</h3>
          <button className="secondary-button">
            <span className="material-symbols-rounded">add</span>
            <span>新建项目</span>
          </button>
        </div>
        <div className="card-content">
          <div className="requirements-list">
            {projects.map(project => (
              <div key={project.id} className="requirement-item">
                <div className={`requirement-status ${project.status}`}></div>
                <div className="requirement-content">
                  <div className="requirement-title">{project.title}</div>
                  <div className="requirement-description">{project.description}</div>
                  <div className="requirement-meta">
                    <span>
                      <span className="material-symbols-rounded">schedule</span>
                      {project.status === 'new' ? '新建' : 
                       project.status === 'in-progress' ? '进行中' : '已完成'}
                    </span>
                    <span>
                      <span className="material-symbols-rounded">calendar_today</span>
                      截止日期：{project.deadline}
                    </span>
                    <span>
                      <span className="material-symbols-rounded">verified</span>
                      完成度：{project.completion}%
                    </span>
                  </div>
                </div>
                <div className="requirement-actions">
                  <button>
                    <span className="material-symbols-rounded">visibility</span>
                  </button>
                  <button>
                    <span className="material-symbols-rounded">edit</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

export default Dashboard;      