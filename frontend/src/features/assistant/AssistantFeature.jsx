import React, { useState } from 'react';
import { MessageSquare, Send } from 'lucide-react';
import { useEvaluation } from '../evaluation/context/EvaluationContext';
import { chatService } from '../../services/chatService';
import ChatPanel from './components/ChatPanel';

export default function AssistantFeature() {
  const { state, dispatch } = useEvaluation();
  const { result, chatMessages, isChatLoading } = state;
  const [chatInput, setChatInput] = useState('');

  if (!result) return null;

  const handleAskAssistant = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !result) return;

    const userQuestion = chatInput.trim();
    setChatInput('');
    
    dispatch({ type: 'CHAT/ADD_MESSAGE', payload: { role: 'user', content: userQuestion } });
    dispatch({ type: 'CHAT/START_LOADING' });

    try {
      const historyPayload = chatMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const payload = {
        filename: result.filename,
        history: historyPayload,
        question: userQuestion,
        skills_evidence: result.evidence?.skills_evidence || []
      };

      const data = await chatService.askAssistant(payload);
      dispatch({ type: 'CHAT/ADD_MESSAGE', payload: {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || []
      }});
    } catch (err) {
      console.error(err);
      dispatch({ type: 'CHAT/ADD_MESSAGE', payload: {
        role: 'assistant',
        content: "I'm sorry, I couldn't reach the backend to answer your question.",
        citations: []
      }});
    } finally {
      dispatch({ type: 'CHAT/STOP_LOADING' });
    }
  };

  return (
    <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex flex-col h-[600px] overflow-hidden">
      {/* Assistant Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-surface-955 flex items-center space-x-2">
        <MessageSquare className="w-4 h-4 text-indigo-600 animate-pulse" />
        <span className="text-sm font-bold text-slate-800 dark:text-slate-200">Recruiter AI Assistant</span>
      </div>

      {/* Chat Messages Panel */}
      <ChatPanel 
        messages={chatMessages} 
        isLoading={isChatLoading} 
      />

      {/* Chat Input Form */}
      <form onSubmit={handleAskAssistant} className="p-3 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-surface-900 flex space-x-2">
        <input
          type="text"
          placeholder="Ask about candidate experience/skills..."
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          disabled={isChatLoading}
          className="flex-1 px-3 py-2 border border-slate-200 dark:border-slate-850 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none transition text-xs font-medium bg-slate-50/50 dark:bg-surface-950 text-slate-800 dark:text-slate-200"
        />
        <button
          type="submit"
          disabled={isChatLoading || !chatInput.trim()}
          className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow transition disabled:opacity-50 flex items-center justify-center"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}
