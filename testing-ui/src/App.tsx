import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import { BookingModal } from './components/BookingModal';
import { ChatArea, ExtendedMessage } from './components/ChatArea';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Booking, HealthInfo, UIError, User } from './types';
import './App.css';

const DEFAULT_USER_ID = '4f904b5b-6a3c-4509-a823-b20ff23af536';

export const App: React.FC = () => {
  const [activeUser, setActiveUser] = useState<User | null>(null);
  const [sessionId, setSessionId] = useState<string>(() => {
    return localStorage.getItem('volta_session_id') || `sess_${Date.now().toString(36)}`;
  });
  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [uiError, setUiError] = useState<UIError | null>(null);
  const [activeBooking, setActiveBooking] = useState<Booking | null>(null);

  // Health probe
  const fetchHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);
    try {
      const data = await api.checkHealth();
      setHealth(data);
    } catch (err: any) {
      setHealth(null);
      setHealthError(err.message || 'Offline');
    } finally {
      setHealthLoading(false);
    }
  };

  // User initialization
  const initUser = async () => {
    const savedUserId = localStorage.getItem('volta_user_id') || DEFAULT_USER_ID;
    try {
      const user = await api.getUser(savedUserId);
      setActiveUser(user);
      localStorage.setItem('volta_user_id', user.id);
    } catch {
      // Fallback: create default user if not found
      try {
        const newUser = await api.createUser(
          'Likith Talla',
          `likith_${Date.now().toString(36)}@example.com`,
          undefined
        );
        setActiveUser(newUser);
        localStorage.setItem('volta_user_id', newUser.id);
      } catch (e: any) {
        console.warn('Could not initialize user:', e);
      }
    }
  };

  useEffect(() => {
    fetchHealth();
    initUser();
  }, []);

  useEffect(() => {
    localStorage.setItem('volta_session_id', sessionId);
  }, [sessionId]);

  const handleNewSession = () => {
    const newId = `sess_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
    setSessionId(newId);
    setMessages([]);
    setUiError(null);
  };

  const handleCreateUser = async (fullName: string, email: string, phone: string) => {
    const newUser = await api.createUser(fullName, email, phone);
    setActiveUser(newUser);
    localStorage.setItem('volta_user_id', newUser.id);
    handleNewSession();
  };

  const handleSwitchUserId = async (userId: string) => {
    const user = await api.getUser(userId);
    setActiveUser(user);
    localStorage.setItem('volta_user_id', user.id);
    handleNewSession();
  };

  const handleSendMessage = async (text: string) => {
    if (!activeUser) {
      setUiError({
        type: 'validation',
        message: 'No active user found. Please create or select a user from the sidebar.',
      });
      return;
    }

    const userMessage: ExtendedMessage = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsSending(true);
    setUiError(null);

    try {
      const chatRes = await api.sendChat(activeUser.id, sessionId, text);

      const assistantMessage: ExtendedMessage = {
        id: `asst_${Date.now()}`,
        role: 'assistant',
        content: chatRes.message.content,
        model_used: chatRes.message.model_used,
        token_count: chatRes.message.token_count || chatRes.usage?.total_tokens,
        created_at: chatRes.message.created_at || new Date().toISOString(),
        recommendation_id: chatRes.recommendation_id,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      let errType: UIError['type'] = 'server_error';
      if (err.status === 408 || err.message?.includes('timed out')) {
        errType = 'timeout';
      } else if (err.status === 0 || err.message?.includes('Unable to connect')) {
        errType = 'offline';
      } else if (err.message?.toLowerCase().includes('gemini') || err.status === 404) {
        errType = 'gemini_error';
      }

      setUiError({
        type: errType,
        message: err.message || 'An unexpected error occurred during chat processing.',
        details: err.data ? JSON.stringify(err.data, null, 2) : undefined,
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleBookRide = async (recommendationId: string, tier: string): Promise<Booking> => {
    const booking = await api.createBooking(recommendationId, tier);
    setActiveBooking(booking);
    return booking;
  };

  return (
    <div className="app-root">
      <Header
        health={health}
        healthLoading={healthLoading}
        healthError={healthError}
        onRefreshHealth={fetchHealth}
        activeUser={activeUser}
        sessionId={sessionId}
      />

      <div className="app-body">
        <Sidebar
          activeUser={activeUser}
          sessionId={sessionId}
          onNewSession={handleNewSession}
          onCreateUser={handleCreateUser}
          onSwitchUserId={handleSwitchUserId}
          messageCount={messages.length}
        />

        <ChatArea
          messages={messages}
          isSending={isSending}
          onSendMessage={handleSendMessage}
          onBookRide={handleBookRide}
          onViewBooking={b => setActiveBooking(b)}
          uiError={uiError}
          onClearError={() => setUiError(null)}
          isBackendOnline={health !== null}
        />
      </div>

      <BookingModal
        booking={activeBooking}
        onClose={() => setActiveBooking(null)}
      />
    </div>
  );
};

// Named alias used by the admin wrapper
export { App as OriginalApp };
export default App;
