import React, { useRef, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatPanel({ messages, isLoading }) {
  const messagesEndRef = useRef(null);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin flex flex-col">
      <div className="flex-1 space-y-4">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 bg-slate-100 dark:bg-surface-850 text-slate-600 dark:text-slate-400 rounded-2xl rounded-bl-none p-3 max-w-[70%] text-xs font-semibold animate-pulse animate-fadeIn">
            <RefreshCw className="w-3 h-3 animate-spin text-indigo-600" />
            <span>Assistant is thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
