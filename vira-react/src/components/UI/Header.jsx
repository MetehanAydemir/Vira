import React from 'react';

const Header = ({ title, subtitle, children }) => {
  return (
    <header className="app-header">
      <div className="header-content">
        {title && <h1 className="header-title">{title}</h1>}
        {subtitle && <p className="header-subtitle">{subtitle}</p>}
      </div>
      
      {children && <div className="header-actions">{children}</div>}
    </header>
  );
};

export default Header;