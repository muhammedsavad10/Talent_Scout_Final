import React from 'react';
import CitationCard from './CitationCard';

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex flex-col max-w-[85%] ${isUser ? 'ml-auto items-end' : 'items-start'}`}>
      <div className={`p-3 rounded-2xl text-xs leading-relaxed ${
        isUser 
          ? 'bg-indigo-600 text-white rounded-br-none font-semibold' 
          : 'bg-slate-100 dark:bg-surface-850 text-slate-800 dark:text-slate-200 rounded-bl-none font-medium'
      }`}>
        {message.content}
      </div>
      
      {!isUser && message.citations && message.citations.length > 0 && (
        <div className="mt-1 space-y-1 w-full">
          {message.citations.map((cite, idx) => (
            <CitationCard key={idx} citation={cite} />
          ))}
        </div>
      )}
    </div>
  );
}
