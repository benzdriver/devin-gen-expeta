import React from 'react';

function Header({ title, sessionId }) {
  return (
    <header className="top-bar">
      <div className="page-title">
        <h1>{title}</h1>
      </div>
      <div className="top-actions">
        <button className="action-button">
          <span className="material-symbols-rounded">notifications</span>
          <span className="notification-badge">3</span>
        </button>
        <button className="action-button">
          <span className="material-symbols-rounded">help</span>
        </button>
        <div className="search-container">
          <input type="text" placeholder="搜索..." className="search-input" />
          <span className="material-symbols-rounded search-icon">search</span>
        </div>
      </div>
    </header>
  );
}

export default Header; 