import React from 'react';
import { Activity, Car, ExternalLink, RefreshCw, UserCheck } from 'lucide-react';
import { HealthInfo, User } from '../types';

interface HeaderProps {
  health: HealthInfo | null;
  healthLoading: boolean;
  healthError: string | null;
  onRefreshHealth: () => void;
  activeUser: User | null;
  sessionId: string;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  healthLoading,
  healthError,
  onRefreshHealth,
  activeUser,
  sessionId,
}) => {
  const isHealthy = health !== null && !healthError;

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="brand-logo">
          <Car className="brand-icon" size={24} />
          <span className="brand-name">VOLTA <span className="brand-accent">AI</span></span>
          <span className="brand-badge">Mobility Assistant</span>
        </div>
      </div>

      <div className="header-center">
        <div className={`health-indicator ${isHealthy ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <span className="status-text">
            {healthLoading
              ? 'Checking backend...'
              : isHealthy
              ? `Backend Online (${health.version})`
              : 'Backend Offline'}
          </span>
          <button
            className="icon-btn"
            onClick={onRefreshHealth}
            title="Refresh Health Status"
            disabled={healthLoading}
          >
            <RefreshCw size={14} className={healthLoading ? 'spin' : ''} />
          </button>
        </div>
      </div>

      <div className="header-right">
        {activeUser && (
          <div className="user-pill" title={`User ID: ${activeUser.id}`}>
            <UserCheck size={14} className="text-accent" />
            <span className="user-pill-name">{activeUser.full_name}</span>
          </div>
        )}
        <div className="session-pill" title={`Session ID: ${sessionId}`}>
          <Activity size={14} />
          <span>{sessionId.slice(0, 12)}...</span>
        </div>
        <a
          href="http://127.0.0.1:8000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="docs-link"
          title="Open FastAPI Swagger Docs"
        >
          <span>API Docs</span>
          <ExternalLink size={14} />
        </a>
      </div>
    </header>
  );
};
