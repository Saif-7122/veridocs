import React from 'react';

const Nav = ({ currentView, onViewChange, hasSession }) => {
  return (
    <div style={{ backgroundColor: '#111111', color: '#FFFFFF', display: 'flex', alignItems: 'center', padding: '16px 24px' }}>
      <div style={{ color: '#CC4125', fontWeight: 'bold', fontSize: '24px', letterSpacing: '1px', marginRight: '40px' }}>
        VERIDOCS
      </div>
      <div style={{ display: 'flex', gap: '24px' }}>
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
                color: active ? '#CC4125' : (disabled ? '#666666' : '#FFFFFF'),
                fontFamily: 'Georgia, serif',
                fontSize: '16px',
                cursor: disabled ? 'not-allowed' : 'pointer',
                textTransform: 'capitalize',
                padding: '4px 0',
                borderBottom: active ? '2px solid #CC4125' : '2px solid transparent'
              }}
            >
              {view}
            </button>
          )
        })}
      </div>
    </div>
  );
};
export default Nav;
