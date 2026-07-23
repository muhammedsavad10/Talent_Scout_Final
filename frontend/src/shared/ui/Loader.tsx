import React from 'react';

export interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  borderRadius?: string;
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '16px',
  borderRadius = '4px',
  className = '',
}) => {
  const styleWidth = typeof width === 'number' ? `${width}px` : width;
  const styleHeight = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={`skeleton ${className}`}
      style={{
        width: styleWidth,
        height: styleHeight,
        borderRadius,
      }}
    />
  );
};

export interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Loader: React.FC<LoaderProps> = ({
  size = 'md',
  className = '',
}) => {
  const dimension = size === 'sm' ? '1.5rem' : size === 'lg' ? '3rem' : '2.25rem';
  
  return (
    <div
      className={`spinner-container ${className}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div
        className="spinner-ring"
        style={{
          width: dimension,
          height: dimension,
          border: '3px solid hsl(var(--border))',
          borderTopColor: 'hsl(var(--ring))',
          borderRadius: '50%',
          animation: 'spin-anim 0.8s linear infinite',
        }}
      />
      <style>{`
        @keyframes spin-anim {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
