import React from 'react';

function Sidebar({ activePage, setActivePage, userData }) {
  const navLinks = [
    { id: 'dashboard', icon: 'dashboard', label: '仪表盘' },
    { id: 'requirements', icon: 'description', label: '需求管理' },
    { id: 'expectations', icon: 'format_list_bulleted', label: '期望管理' },
    { id: 'code-generation', icon: 'code', label: '代码生成' },
    { id: 'validation', icon: 'verified', label: '验证结果' },
    { id: 'memory', icon: 'database', label: '记忆系统' },
    { id: 'semantic-mediator', icon: 'swap_horiz', label: '语义中介层' },
    { id: 'settings', icon: 'settings', label: '系统设置' },
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
            <a href={`#${link.id}`} onClick={(e) => {
              e.preventDefault();
              setActivePage(link.id);
            }}>
              <span className="material-symbols-rounded">{link.icon}</span>
              <span>{link.label}</span>
            </a>
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