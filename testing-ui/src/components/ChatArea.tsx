import React, { useEffect, useRef, useState } from 'react';
import {
  AlertCircle,
  Bot,
  Car,
  CornerDownLeft,
  Cpu,
  Loader2,
  User as UserIcon,
  WifiOff,
} from 'lucide-react';
import { Booking, ChatMessage, UIError } from '../types';
import { QuickPrompts } from './QuickPrompts';
import { RecommendationCard } from './RecommendationCard';

export interface ExtendedMessage extends ChatMessage {
  id: string;
  recommendation_id?: string | null;
}

interface ChatAreaProps {
  messages: ExtendedMessage[];
  isSending: boolean;
  onSendMessage: (text: string) => Promise<void>;
  onBookRide: (recommendationId: string, tier: string) => Promise<Booking>;
  onViewBooking: (booking: Booking) => void;
  uiError: UIError | null;
  onClearError: () => void;
  isBackendOnline: boolean;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isSending,
  onSendMessage,
  onBookRide,
  onViewBooking,
  uiError,
  onClearError,
  isBackendOnline,
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isSending) return;
    const text = inputText.trim();
    setInputText('');
    await onSendMessage(text);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <main className="chat-container">
      {/* Offline Warning Banner */}
      {!isBackendOnline && (
        <div className="offline-banner">
          <WifiOff size={16} />
          <span>
            Volta Backend server appears offline. Make sure Uvicorn is running on <code>http://127.0.0.1:8000</code>.
          </span>
        </div>
      )}

      {/* Dynamic API Error Banner */}
      {uiError && (
        <div className={`error-banner ${uiError.type}`}>
          <div className="error-banner-content">
            <AlertCircle size={18} className="error-icon" />
            <div className="error-text-block">
              <strong className="error-title">
                {uiError.type === 'timeout'
                  ? 'Request Timeout'
                  : uiError.type === 'gemini_error'
                  ? 'AI Provider Issue'
                  : 'API Communication Error'}
              </strong>
              <p className="error-msg">{uiError.message}</p>
              {uiError.details && (
                <details className="error-details">
                  <summary>View Technical Details</summary>
                  <pre>{uiError.details}</pre>
                </details>
              )}
            </div>
          </div>
          <button className="error-close-btn" onClick={onClearError}>
            Dismiss
          </button>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="messages-scroll-area">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <div className="empty-avatar">
              <Car size={36} className="text-accent" />
            </div>
            <h2>Welcome to Volta AI Mobility</h2>
            <p>
              Your AI-powered urban ride-booking and route assistant. Ask to book a ride,
              explore vehicle options, or estimate trip fares.
            </p>
            <QuickPrompts
              onSelectPrompt={p => {
                setInputText(p);
                inputRef.current?.focus();
              }}
              disabled={isSending}
            />
          </div>
        ) : (
          messages.map(msg => (
            <div
              key={msg.id}
              className={`message-row ${msg.role === 'user' ? 'user' : 'assistant'}`}
            >
              <div className="message-avatar">
                {msg.role === 'user' ? (
                  <UserIcon size={18} />
                ) : (
                  <Bot size={18} className="text-accent" />
                )}
              </div>

              <div className="message-bubble-wrap">
                <div className="message-meta-header">
                  <span className="sender-name">
                    {msg.role === 'user' ? 'You' : 'Volta AI'}
                  </span>
                  {msg.model_used && (
                    <span className="model-tag" title="Inference Model">
                      <Cpu size={12} />
                      <span>{msg.model_used}</span>
                    </span>
                  )}
                  {msg.token_count && (
                    <span className="token-tag">
                      {msg.token_count} tokens
                    </span>
                  )}
                  {msg.created_at && (
                    <span className="timestamp">
                      {new Date(msg.created_at).toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  )}
                </div>

                <div className="message-bubble">
                  <div className="message-content-text">
                    {msg.content}
                  </div>
                </div>

                {/* Interactive Ride Recommendation Card when attached */}
                {msg.role === 'assistant' && msg.recommendation_id && (
                  <RecommendationCard
                    recommendationId={msg.recommendation_id}
                    onBook={onBookRide}
                    onViewBooking={onViewBooking}
                  />
                )}
              </div>
            </div>
          ))
        )}

        {/* AI Typing / Reasoning Indicator */}
        {isSending && (
          <div className="message-row assistant">
            <div className="message-avatar">
              <Bot size={18} className="text-accent" />
            </div>
            <div className="message-bubble-wrap">
              <div className="message-bubble typing">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="typing-label">Volta AI is thinking & calculating transit routes...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <footer className="chat-input-footer">
        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            ref={inputRef}
            type="text"
            className="chat-input-field"
            placeholder="Ask Volta AI to book a ride, compare electric vehicles, or check ETA..."
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSending}
          />
          <button
            type="submit"
            className="send-btn"
            disabled={!inputText.trim() || isSending}
            title="Send Message"
          >
            {isSending ? (
              <Loader2 size={18} className="spin" />
            ) : (
              <>
                <span>Send</span>
                <CornerDownLeft size={16} />
              </>
            )}
          </button>
        </form>
      </footer>
    </main>
  );
};
