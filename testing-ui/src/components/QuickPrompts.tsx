import React from 'react';
import { Sparkles } from 'lucide-react';

interface QuickPromptsProps {
  onSelectPrompt: (prompt: string) => void;
  disabled?: boolean;
}

const PROMPTS = [
  { icon: '✈️', text: 'I need a ride to the airport. What options do you have?' },
  { icon: '⚡', text: 'Tell me about Volta EV and eco-friendly rides.' },
  { icon: '🏙️', text: 'Can you recommend a vehicle for 4 people with luggage?' },
  { icon: '⏱️', text: 'What is the fastest pickup ETA right now?' },
];

export const QuickPrompts: React.FC<QuickPromptsProps> = ({ onSelectPrompt, disabled }) => {
  return (
    <div className="quick-prompts">
      <div className="quick-prompts-title">
        <Sparkles size={14} className="text-accent" />
        <span>Quick Test Prompts</span>
      </div>
      <div className="prompts-grid">
        {PROMPTS.map((p, i) => (
          <button
            key={i}
            className="prompt-chip"
            onClick={() => onSelectPrompt(p.text)}
            disabled={disabled}
          >
            <span className="prompt-icon">{p.icon}</span>
            <span className="prompt-text">{p.text}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
