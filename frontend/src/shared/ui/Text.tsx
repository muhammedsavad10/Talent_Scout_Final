import React from 'react';

export interface TextProps extends React.HTMLAttributes<HTMLParagraphElement> {
  variant?: 'body' | 'small' | 'muted';
}

export const Text: React.FC<TextProps> = ({
  children,
  variant = 'body',
  className = '',
  ...props
}) => {
  const getStyleClass = () => {
    if (variant === 'small') return 'text-sm';
    if (variant === 'muted') return 'text-muted-foreground';
    return '';
  };

  return (
    <p
      className={`text-body ${getStyleClass()} ${className}`}
      style={{
        lineHeight: 1.5,
        color: variant === 'muted' ? 'hsl(var(--muted-foreground))' : 'inherit',
        fontSize: variant === 'small' ? '13px' : '14px',
      }}
      {...props}
    >
      {children}
    </p>
  );
};
export default Text;
