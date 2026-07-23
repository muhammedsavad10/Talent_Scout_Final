import React from 'react';

export interface HeadingProps extends React.HTMLAttributes<HTMLHeadingElement> {
  level?: 1 | 2 | 3 | 4 | 5 | 6;
}

export const Heading: React.FC<HeadingProps> = ({
  children,
  level = 2,
  className = '',
  ...props
}) => {
  const Tag = `h${level}` as const;
  return (
    <Tag className={`heading-level-${level} ${className}`} {...props}>
      {children}
    </Tag>
  );
};
export default Heading;
