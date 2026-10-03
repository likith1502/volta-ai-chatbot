import React, { useEffect, useRef, useState } from 'react';
import {
  AlertCircle,
  Bot,
  Car,
  Loader2,
  MessageSquare,
  RefreshCw,
  Send,
  WifiOff,
  X,
} from 'lucide-react';
import { api } from '../api/client';
import { RideState, UIError, User } from '../types';
import { formatTimeIST } from '../utils/india';
import { RideCard } from './RideCard';
import './CustomerChatbot.css';


interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  model_used?: string | null;
  token_count?: number | null;
  recommendation_id?: string | null;
  ride?: RideState | null;
}

const SUGGESTED_PROMPTS = [
  { icon: '🚕', text: 'Book a cab', full: 'Book a cab' },
  { icon: '✈️', text: 'Kukatpally to airport fare', full: 'How much from Kukatpally to airport?' },
  { icon: '📍', text: 'Secunderabad → Gachibowli', full: 'Book a cab from Secunderabad to Gachibowli' },
  { icon: '💳', text: 'Can I pay through UPI?', full: 'Can I pay through UPI?' },
];

export const CustomerChatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [uiError, setUiError] = useState<UIError | null>(null);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);
  const [activeUser, setActiveUser] = useState<User | null>(null);
  const [sessionId] = useState<string>(() => {
    return localStorage.getItem('volta_customer_session') || `sess_${Date.now().toString(36)}`;
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Save session
  useEffect(() => {
    localStorage.setItem('volta_customer_session', sessionId);
  }, [sessionId]);

  // Check backend health
  const checkHealth = async () => {
    try {
      await api.checkHealth();
      setIsBackendOnline(true);
    } catch {
      setIsBackendOnline(false);
    }
  };

  // Initialize user
  const initUser = async () => {
    // TEMPORARY guest identity until VOLTA app login (phone OTP) is integrated.
    const savedUserId = localStorage.getItem('volta_customer_user_id');
    try {
      if (!savedUserId) throw new Error('no saved user');
      const user = await api.getUser(savedUserId);
      setActiveUser(user);
    } catch {
      try {
        const newUser = await api.createUser(
          'VOLTA Guest',
          `guest_${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}@guest.example.com`
        );
        setActiveUser(newUser);
        localStorage.setItem('volta_customer_user_id', newUser.id);
      } catch (e) {
        console.warn('Could not initialize customer user:', e);
      }
    }
  };

  useEffect(() => {
    checkHealth();
    initUser();
  }, []);

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSendMessage = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;

    if (!activeUser) {
      setUiError({
        type: 'validation',
        message: 'Session is still initializing. Please wait a moment and try again.',
      });
      return;
    }

    const userMessage: Message = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content: trimmed,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsSending(true);
    setUiError(null);

    try {
      const chatRes = await api.sendChat(activeUser.id, sessionId, trimmed);
      const assistantMessage: Message = {
        id: `asst_${Date.now()}`,
        role: 'assistant',
        content: chatRes.message.content,
        model_used: chatRes.message.model_used,
        token_count: chatRes.message.token_count || chatRes.usage?.total_tokens,
        created_at: chatRes.message.created_at || new Date().toISOString(),
        recommendation_id: chatRes.recommendation_id,
        ride: chatRes.ride ?? null,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      let errType: UIError['type'] = 'server_error';
      if (err.status === 408 || err.message?.includes('timed out')) {
        errType = 'timeout';
      } else if (err.status === 0 || err.message?.includes('Unable to connect')) {
        errType = 'offline';
        setIsBackendOnline(false);
      } else if (err.message?.toLowerCase().includes('gemini') || err.status === 404) {
        errType = 'gemini_error';
      }
      // Customers never see raw server payloads.
      if (err.data) console.warn('Chat error details:', err.data);
      setUiError({
        type: errType,
        message:
          errType === 'offline' || errType === 'timeout'
            ? err.message
            : 'Sorry, something went wrong. Please try again.',
      });
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    handleSendMessage(inputText);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handlePromptClick = (prompt: typeof SUGGESTED_PROMPTS[0]) => {
    handleSendMessage(prompt.full);
  };

  const lastRideMsgId = [...messages].reverse().find(m => m.ride)?.id;

  const getErrorTitle = (type: UIError['type']) => {
    switch (type) {
      case 'timeout': return 'Request timed out';
      case 'offline': return 'Cannot reach VOLTA servers';
      case 'gemini_error': return 'AI service issue';
      default: return 'Something went wrong';
    }
  };

  return (
    <div className="cb-root">
      {/* Header */}
      <header className="cb-header">
        <div className="cb-header-brand">
          <div className="cb-logo">
            <Car size={22} />
          </div>
          <div className="cb-brand-text">
            <span className="cb-brand-name">VOLTA <span className="cb-brand-accent">AI</span></span>
            <span className="cb-brand-sub">Cab booking &amp; help · India</span>
          </div>
        </div>
        <div className="cb-header-right">
          {isBackendOnline === null ? (
            <div className="cb-status cb-status--checking">
              <Loader2 size={12} className="cb-spin" />
              <span>Connecting...</span>
            </div>
          ) : isBackendOnline ? (
            <div className="cb-status cb-status--online">
              <span className="cb-status-dot" />
              <span>Online</span>
            </div>
          ) : (
            <div className="cb-status cb-status--offline">
              <WifiOff size={12} />
              <span>Offline</span>
              <button className="cb-retry-btn" onClick={checkHealth} title="Retry">
                <RefreshCw size={11} />
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Offline banner */}
      {isBackendOnline === false && (
        <div className="cb-offline-bar">
          <WifiOff size={14} />
          <span>
            We're having trouble connecting to VOLTA. Please try again in a moment.
          </span>
          <button className="cb-retry-text" onClick={() => { checkHealth(); initUser(); }}>
            Retry
          </button>
        </div>
      )}

      {/* Error banner */}
      {uiError && (
        <div className={`cb-error-bar cb-error-bar--${uiError.type}`}>
          <AlertCircle size={15} className="cb-error-icon" />
          <div className="cb-error-body">
            <strong>{getErrorTitle(uiError.type)}</strong>
            <p>{uiError.message}</p>
            {uiError.details && (
              <details className="cb-error-details">
                <summary>Details</summary>
                <pre>{uiError.details}</pre>
              </details>
            )}
          </div>
          <button className="cb-error-dismiss" onClick={() => setUiError(null)}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Chat messages */}
      <div className="cb-messages">
        {messages.length === 0 ? (
          /* Welcome screen */
          <div className="cb-welcome">
            <div className="cb-welcome-orb">
              <Bot size={40} />
            </div>
            <h1 className="cb-welcome-title">Welcome to VOLTA!</h1>
            <p className="cb-welcome-sub">
              Namaste! I can book you a cab and answer questions about VOLTA.
              Try “Airport ki cab kavali” or “Secunderabad to Gachibowli”.
            </p>
            <div className="cb-suggestions">
              {SUGGESTED_PROMPTS.map((p, i) => (
                <button
                  key={i}
                  className="cb-suggestion-chip"
                  onClick={() => handlePromptClick(p)}
                  disabled={isSending || !activeUser}
                >
                  <span className="cb-suggestion-icon">{p.icon}</span>
                  <span>{p.text}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map(msg => (
              <div
                key={msg.id}
                className={`cb-message-row ${msg.role === 'user' ? 'cb-message-row--user' : 'cb-message-row--assistant'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="cb-avatar cb-avatar--bot">
                    <Bot size={16} />
                  </div>
                )}

                <div className="cb-bubble-wrap">
                  <div className={`cb-bubble ${msg.role === 'user' ? 'cb-bubble--user' : 'cb-bubble--assistant'}`}>
                    <div className="cb-bubble-text">{msg.content}</div>
                  </div>

                  {msg.role === 'assistant' && (
                    <span className="cb-timestamp">
                      {formatTimeIST(msg.created_at)}
                    </span>
                  )}
                  {msg.role === 'user' && (
                    <span className="cb-timestamp cb-timestamp--right">
                      {formatTimeIST(msg.created_at)}
                    </span>
                  )}

                  {/* Ride card (data comes from the backend, never hardcoded) */}
                  {msg.role === 'assistant' && msg.ride && (
                    <RideCard
                      ride={msg.ride}
                      isLatest={msg.id === lastRideMsgId}
                      disabled={isSending}
                      onSend={handleSendMessage}
                    />
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="cb-avatar cb-avatar--user">
                    <MessageSquare size={15} />
                  </div>
                )}
              </div>
            ))}

            {/* Typing indicator */}
            {isSending && (
              <div className="cb-message-row cb-message-row--assistant">
                <div className="cb-avatar cb-avatar--bot">
                  <Bot size={16} />
                </div>
                <div className="cb-bubble-wrap">
                  <div className="cb-bubble cb-bubble--assistant cb-bubble--typing">
                    <div className="cb-typing-dots">
                      <span />
                      <span />
                      <span />
                    </div>
                    <span className="cb-typing-label">VOLTA is typing…</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <footer className="cb-input-area">
        <form className="cb-input-form" onSubmit={handleSubmit}>
          <textarea
            ref={inputRef}
            className="cb-input-field"
            placeholder="Book a cab or ask about VOLTA…"
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isSending}
            rows={1}
          />
          <button
            type="submit"
            className="cb-send-btn"
            disabled={!inputText.trim() || isSending || !activeUser}
            title="Send message"
          >
            {isSending ? (
              <Loader2 size={18} className="cb-spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </form>
        <div className="cb-input-hint">
          Press <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line
        </div>
      </footer>

    </div>
  );
};

export default CustomerChatbot;
