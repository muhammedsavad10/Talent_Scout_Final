import React, { useState, useRef, useEffect } from 'react';
import { useAssistantAsk } from '../hooks/useAssistantAsk';
import { X, Send, Bot, User } from 'lucide-react';
import { Heading, Text, Button } from '@/shared/ui';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: string[];
  confidence?: string | undefined;
  matchType?: string | undefined;
  verification?: string | undefined;
}

interface AssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  candidateName: string;
  candidateId: string;
  onCitationClick?: (citationText: string) => void;
}

export const AssistantDrawer: React.FC<AssistantDrawerProps> = ({
  isOpen,
  onClose,
  candidateName,
  candidateId,
  onCitationClick,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: `Hello! I am the TalentScout Evaluation Copilot. Ask me anything about ${candidateName}'s resume, work history, skill fit, or gaps.`,
    },
  ]);
  const [inputVal, setInputVal] = useState('');
  const chatEndRef = useRef<HTMLDivElement>(null);
  const askMutation = useAssistantAsk();

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    const query = inputVal.trim();
    if (!query) return;

    // 1. Add User Message
    const userMsgId = `msg-${Date.now()}`;
    setMessages((prev) => [...prev, { id: userMsgId, sender: 'user', text: query }]);
    setInputVal('');

    // 2. Trigger mutation ask with candidateId
    askMutation.mutate(
      { query, candidateId },
      {
        onSuccess: (data) => {
          setMessages((prev) => [
            ...prev,
            {
              id: `msg-${Date.now()}-ai`,
              sender: 'assistant',
              text: data.answer,
              citations: data.citations,
              confidence: data.confidence,
              matchType: data.match_type,
              verification: data.interview_verification,
            },
          ]);
        },
        onError: (error) => {
          setMessages((prev) => [
            ...prev,
            {
              id: `msg-${Date.now()}-err`,
              sender: 'assistant',
              text: `Error: ${error.message || 'System failed to contact parser swarm.'}`,
            },
          ]);
        },
      }
    );
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: '450px',
        maxWidth: '100vw',
        background: 'hsl(var(--card))',
        borderLeft: '1px solid hsl(var(--border))',
        boxShadow: 'var(--shadow-2xl)',
        zIndex: 500,
        display: 'flex',
        flexDirection: 'column',
        animation: 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
      }}
    >
      {/* Header Panel */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid hsl(var(--border))',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Bot size={20} style={{ color: 'hsl(var(--primary))' }} />
          <div>
            <Heading level={3} style={{ fontSize: '15px', margin: 0 }}>Copilot AI Assistant</Heading>
            <Text style={{ fontSize: '11px', color: 'hsl(var(--muted-foreground))' }}>Querying {candidateName}</Text>
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ background: 'transparent', border: 'none', color: 'hsl(var(--muted-foreground))', cursor: 'pointer', padding: '4px' }}
          aria-label="Close assistant drawer"
        >
          <X size={20} />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg) => {
          const isAi = msg.sender === 'assistant';
          return (
            <div
              key={msg.id}
              style={{
                display: 'flex',
                gap: '10px',
                flexDirection: isAi ? 'row' : 'row-reverse',
                alignItems: 'flex-start',
              }}
            >
              {/* Profile Icon */}
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: isAi ? 'hsla(var(--primary), 0.1)' : 'hsla(var(--foreground), 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: isAi ? 'hsl(var(--primary))' : 'inherit',
                flexShrink: 0,
              }}>
                {isAi ? <Bot size={16} /> : <User size={16} />}
              </div>

              {/* Text Bubble */}
              <div style={{
                maxWidth: '75%',
                padding: '12px 14px',
                borderRadius: 'var(--radius)',
                background: isAi ? 'hsl(var(--secondary))' : 'linear-gradient(135deg, hsl(var(--primary)), #8b5cf6)',
                color: isAi ? 'hsl(var(--foreground))' : '#ffffff',
                fontSize: '13px',
                lineHeight: '1.5',
                wordBreak: 'break-word',
              }}>
                {msg.text}

                {/* Grounding metadata badges */}
                {isAi && msg.confidence && (
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px', fontSize: '10px' }}>
                    <span style={{
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: msg.confidence === 'High' ? 'hsla(var(--success), 0.12)' : 'hsla(var(--warning), 0.12)',
                      color: msg.confidence === 'High' ? 'hsl(var(--success))' : 'hsl(var(--warning))',
                      fontWeight: 700
                    }}>
                      Confidence: {msg.confidence}
                    </span>
                    <span style={{
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: 'hsla(var(--primary), 0.12)',
                      color: 'hsl(var(--primary))',
                      fontWeight: 700
                    }}>
                      Match: {msg.matchType || 'N/A'}
                    </span>
                  </div>
                )}

                {isAi && msg.verification && (
                  <div style={{
                    marginTop: '8px',
                    padding: '6px 10px',
                    background: 'hsla(var(--foreground), 0.04)',
                    borderLeft: '3px solid hsl(var(--accent))',
                    fontSize: '11px',
                    borderRadius: '2px',
                    color: 'hsl(var(--muted-foreground))'
                  }}>
                    <strong>Screener Probe:</strong> {msg.verification}
                  </div>
                )}
                
                {/* Citations list */}
                {msg.citations && msg.citations.length > 0 && (
                  <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid hsla(var(--foreground), 0.1)', fontSize: '11px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span style={{ fontWeight: 600 }}>References / Proof (Click to locate):</span>
                    {msg.citations.map((cite, idx) => (
                      <button
                        key={idx}
                        onClick={() => onCitationClick && onCitationClick(cite)}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: 'hsl(var(--accent))',
                          textAlign: 'left',
                          cursor: 'pointer',
                          padding: '2px 0',
                          fontSize: '11px',
                          display: 'block',
                          textDecoration: 'underline',
                          width: '100%',
                          outline: 'none',
                        }}
                      >
                        &bull; {cite}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
        {askMutation.isPending && (
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: 'hsla(var(--primary), 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'hsl(var(--primary))',
            }}>
              <Bot size={16} />
            </div>
            <div style={{ padding: '8px 12px', borderRadius: 'var(--radius)', background: 'hsl(var(--secondary))' }}>
              <span style={{ fontSize: '12px', color: 'hsl(var(--muted-foreground))' }}>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input box Form Panel */}
      <form
        onSubmit={handleSend}
        style={{
          padding: '16px 20px',
          borderTop: '1px solid hsl(var(--border))',
          display: 'flex',
          gap: '10px',
          background: 'hsl(var(--card))',
        }}
      >
        <input
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          placeholder="Ask a question..."
          disabled={askMutation.isPending}
          style={{
            flex: 1,
            padding: '10px 14px',
            background: 'hsl(var(--secondary))',
            border: '1px solid hsl(var(--border))',
            borderRadius: 'var(--radius)',
            color: '#ffffff',
            fontSize: '13px',
            outline: 'none',
          }}
        />
        <Button
          type="submit"
          variant="primary"
          size="sm"
          disabled={askMutation.isPending || !inputVal.trim()}
          style={{ width: '40px', height: '38px', padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          <Send size={16} />
        </Button>
      </form>

      {/* Slide in animation styles */}
      <style>{`
        @keyframes slideIn {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }
      `}</style>
    </div>
  );
};
export default AssistantDrawer;
