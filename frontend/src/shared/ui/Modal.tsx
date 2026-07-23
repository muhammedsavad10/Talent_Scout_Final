import React from 'react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid hsl(var(--border))', paddingBottom: '12px' }}>
          {title && <h3 style={{ margin: 0, fontSize: '18px' }}>{title}</h3>}
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'hsl(var(--muted-foreground))',
              cursor: 'pointer',
              fontSize: '18px',
              fontWeight: 'bold',
            }}
          >
            &times;
          </button>
        </div>
        <div style={{ paddingTop: '12px' }}>
          {children}
        </div>
      </div>
    </div>
  );
};
