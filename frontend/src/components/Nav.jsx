import React from 'react';

const Nav = ({ currentView, onViewChange, hasSession }) => {
  return (
    <nav style={{ 
      backgroundColor: 'var(--bg-dark)', 
      color: 'white', 
      display: 'flex', 
      alignItems: 'center', 
      padding: '16px 40px',
      borderBottom: '4px solid var(--primary)'
    }}>
      <div style={{ 
        color: 'var(--primary)', 
        fontWeight: 'bold', 
        fontSize: '24px', 
        letterSpacing: '1px', 
        marginRight: '60px' 
      }}>
        VERIDOCS
      </div>
      <div style={{ display: 'flex', gap: '32px' }}>
        {['upload', 'chat', 'compare', 'report'].map(view => {
          const disabled = view !== 'upload' && !hasSession;
          const active = currentView === view;
          return (
            <button
              key={view}
              disabled={disabled}
              onClick={() => !disabled && onViewChange(view)}
              style={{
                background: 'none',
                border: 'none',
                color: active ? 'white' : (disabled ? '#555' : '#aaa'),
                fontFamily: 'inherit',
                fontSize: '16px',
                cursor: disabled ? 'not-allowed' : 'pointer',
                textTransform: 'capitalize',
                padding: '4px 0',
                borderBottom: active ? '2px solid white' : '2px solid transparent',
                transition: 'var(--transition)'
              }}
            >
              {view}
            </button>
          )
        })}
      </div>
    </nav>
  );
};
export default Nav;
