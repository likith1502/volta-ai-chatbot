import React, { useState } from 'react';
import {
  CheckCircle2,
  MessageSquarePlus,
  User,
  UserPlus,
  Users,
} from 'lucide-react';
import { User as UserType } from '../types';

interface SidebarProps {
  activeUser: UserType | null;
  sessionId: string;
  onNewSession: () => void;
  onCreateUser: (fullName: string, email: string, phone: string) => Promise<void>;
  onSwitchUserId: (userId: string) => Promise<void>;
  messageCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeUser,
  sessionId,
  onNewSession,
  onCreateUser,
  onSwitchUserId,
  messageCount,
}) => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSwitchModal, setShowSwitchModal] = useState(false);
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [switchId, setSwitchId] = useState('');
  const [loading, setLoading] = useState(false);
  const [userError, setUserError] = useState<string | null>(null);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !email.trim()) return;
    setLoading(true);
    setUserError(null);
    try {
      await onCreateUser(fullName, email, phone);
      setShowCreateModal(false);
      setFullName('');
      setEmail('');
      setPhone('');
    } catch (err: any) {
      setUserError(err.message || 'Failed to create user');
    } finally {
      setLoading(false);
    }
  };

  const handleSwitch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!switchId.trim()) return;
    setLoading(true);
    setUserError(null);
    try {
      await onSwitchUserId(switchId.trim());
      setShowSwitchModal(false);
      setSwitchId('');
    } catch (err: any) {
      setUserError(err.message || 'Failed to fetch user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <aside className="app-sidebar">
      {/* Action Button: New Chat */}
      <div className="sidebar-action-wrap">
        <button className="new-chat-btn" onClick={onNewSession}>
          <MessageSquarePlus size={18} />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Active User Card */}
      <div className="sidebar-section">
        <div className="section-label">Active User (Caller Context)</div>
        {activeUser ? (
          <div className="user-card">
            <div className="user-avatar">
              <User size={20} />
            </div>
            <div className="user-info">
              <span className="user-name">{activeUser.full_name}</span>
              <span className="user-email">{activeUser.email}</span>
              <span className="user-id-code" title={activeUser.id}>
                ID: {activeUser.id.slice(0, 8)}...
              </span>
            </div>
          </div>
        ) : (
          <div className="user-empty-notice">No user context loaded.</div>
        )}

        <div className="user-actions-row">
          <button
            className="secondary-btn-sm"
            onClick={() => {
              setUserError(null);
              setShowCreateModal(true);
            }}
          >
            <UserPlus size={14} />
            <span>Create User</span>
          </button>
          <button
            className="secondary-btn-sm"
            onClick={() => {
              setUserError(null);
              setShowSwitchModal(true);
            }}
          >
            <Users size={14} />
            <span>Switch ID</span>
          </button>
        </div>
      </div>

      {/* Session Diagnostics */}
      <div className="sidebar-section">
        <div className="section-label">Session Information</div>
        <div className="session-card">
          <div className="session-item">
            <span className="session-label">Session ID:</span>
            <span className="session-val code-font" title={sessionId}>
              {sessionId}
            </span>
          </div>
          <div className="session-item">
            <span className="session-label">Turns in Session:</span>
            <span className="session-val highlight">{messageCount}</span>
          </div>
          <div className="session-item">
            <span className="session-label">Channel Source:</span>
            <span className="session-val">WEB (REST v1)</span>
          </div>
        </div>
      </div>

      {/* Architecture Badges */}
      <div className="sidebar-footer">
        <div className="footer-title">VOLTA Architecture Tiers</div>
        <ul className="footer-specs">
          <li><CheckCircle2 size={12} className="text-accent" /> FastAPI ASGI Server</li>
          <li><CheckCircle2 size={12} className="text-accent" /> Async PostgreSQL 15+</li>
          <li><CheckCircle2 size={12} className="text-accent" /> Google Gemini 3.6 Flash</li>
          <li><CheckCircle2 size={12} className="text-accent" /> Provider-Agnostic Engine</li>
        </ul>
      </div>

      {/* Modal: Create User */}
      {showCreateModal && (
        <div className="modal-backdrop" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content sm" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create User Context</h3>
            </div>
            <form onSubmit={handleCreate} className="modal-form">
              {userError && <div className="form-error">{userError}</div>}
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  placeholder="e.g. Alex Rivera"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  placeholder="alex@volta.example.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone Number</label>
                <input
                  type="text"
                  placeholder="e.g. 5550192837"
                  value={phone}
                  onChange={e => setPhone(e.target.value)}
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="primary-btn" disabled={loading}>
                  {loading ? 'Creating...' : 'Create in Database'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Switch User ID */}
      {showSwitchModal && (
        <div className="modal-backdrop" onClick={() => setShowSwitchModal(false)}>
          <div className="modal-content sm" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Switch to Existing User ID</h3>
            </div>
            <form onSubmit={handleSwitch} className="modal-form">
              {userError && <div className="form-error">{userError}</div>}
              <div className="form-group">
                <label>User UUID</label>
                <input
                  type="text"
                  placeholder="4f904b5b-6a3c-4509-a823-b20ff23af536"
                  value={switchId}
                  onChange={e => setSwitchId(e.target.value)}
                  required
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={() => setShowSwitchModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="primary-btn" disabled={loading}>
                  {loading ? 'Fetching...' : 'Set Active User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </aside>
  );
};
