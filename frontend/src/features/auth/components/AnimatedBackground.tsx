import React from 'react';
import { motion } from 'framer-motion';

export const AnimatedBackground: React.FC = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none select-none z-0 bg-slate-950">
      {/* Precision Dot Mesh Background */}
      <div 
        className="absolute inset-0 opacity-[0.05]" 
        style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.7) 1px, transparent 0)`,
          backgroundSize: '28px 28px'
        }}
      />

      {/* Top Left Deep Indigo Glow */}
      <motion.div
        animate={{
          x: [0, 20, -10, 0],
          y: [0, -20, 10, 0],
          scale: [1, 1.05, 0.95, 1],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute -top-36 -left-36 w-[550px] h-[550px] bg-indigo-600/12 rounded-full blur-[140px]"
      />

      {/* Bottom Right Cyan/Purple Glow */}
      <motion.div
        animate={{
          x: [0, -25, 15, 0],
          y: [0, 20, -20, 0],
          scale: [1, 0.95, 1.05, 1],
        }}
        transition={{
          duration: 22,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute -bottom-36 -right-36 w-[600px] h-[600px] bg-purple-600/12 rounded-full blur-[150px]"
      />
    </div>
  );
};

export default AnimatedBackground;
