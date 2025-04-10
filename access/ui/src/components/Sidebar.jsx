import React from 'react';
import { Link } from 'react-router-dom';

function Sidebar({ activePage, setActivePage, userData }) {
  const navLinks = [
    { id: 'dashboard', icon: 'dashboard', label: '仪表盘', path: '/' },
    { id: 'chat-requirements', icon: 'chat', label: '统一需求对话', path: '/chat-requirements' },
    { id: 'requirements', icon: 'description', label: '传统需求管理', path: '/requirements' },
    { id: 'direct-chat', icon: 'forum', label: '直接聊天测试', path: '/direct-chat' },
    { id: 'expectations', icon: 'format_list_bulleted', label: '期望管理', path: '/expectations' },
    { id: 'code-generation', icon: 'code', label: '代码生成', path: '/code-generation' },
    { id: 'validation', icon: 'verified', label: '验证结果', path: '/validation' },
    { id: 'memory', icon: 'database', label: '记忆系统', path: '/memory' },
    { id: 'semantic-mediator', icon: 'swap_horiz', label: '语义中介层', path: '/semantic-mediator' },
    { id: 'settings', icon: 'settings', label: '系统设置', path: '/settings' },
  ];

  return (
    <nav className="sidebar">
      <div className="logo">
        <span className="logo-icon">E</span>
        <span className="logo-text">Expeta 2.0</span>
      </div>
      <ul className="nav-links">
        {navLinks.map(link => (
          <li key={link.id} className={`nav-item ${activePage === link.id ? 'active' : ''}`}>
            <Link to={link.path} onClick={(e) => {
              setActivePage(link.id);
            }}>
              <span className="material-symbols-rounded">{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          </li>
        ))}
      </ul>
      <div className="user-info">
        <div className="user-avatar">
          <span className="material-symbols-rounded">person</span>
        </div>
        <div className="user-details">
          <span className="user-name">{userData.name}</span>
          <span className="user-role">{userData.role}</span>
        </div>
      </div>
    </nav>
  );
}

export default Sidebar;         