import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string | undefined;
  error?: string | undefined;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  id,
  className = '',
  ...props
}) => {
  return (
    <div className="form-group">
      {label && <label htmlFor={id} className="form-label">{label}</label>}
      <input
        id={id}
        className={`input-field ${error ? 'border-destructive' : ''} ${className}`}
        {...props}
      />
      {error && <span style={{ color: 'hsl(var(--destructive))', fontSize: '12px', marginTop: '4px' }}>{error}</span>}
    </div>
  );
};

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string | undefined;
  error?: string | undefined;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  id,
  className = '',
  rows = 4,
  ...props
}) => {
  return (
    <div className="form-group">
      {label && <label htmlFor={id} className="form-label">{label}</label>}
      <textarea
        id={id}
        rows={rows}
        className={`input-field ${error ? 'border-destructive' : ''} ${className}`}
        {...props}
      />
      {error && <span style={{ color: 'hsl(var(--destructive))', fontSize: '12px', marginTop: '4px' }}>{error}</span>}
    </div>
  );
};
export default Input;
