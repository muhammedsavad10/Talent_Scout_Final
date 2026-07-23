import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'destructive' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  className = '',
  disabled,
  ...props
}) => {
  return (
    <button
      className={`btn btn-${variant} btn-${size} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="spinner-border" style={{
          width: '1em',
          height: '1em',
          border: '2px solid currentColor',
          borderRightColor: 'transparent',
          borderRadius: '50%',
          display: 'inline-block',
          animation: 'spin 0.75s linear infinite',
          marginRight: '8px'
        }} />
      ) : null}
      {children}
    </button>
  );
};
