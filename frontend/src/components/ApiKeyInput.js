import React, { useState } from 'react';
import { Key, Eye, EyeOff, Zap, Gift } from 'lucide-react';
import './ApiKeyInput.css';

const ApiKeyInput = ({ apiKey, setApiKey, freeTierAvailable, usageInfo }) => {
  const [showKey, setShowKey] = useState(false);

  return (
    <div className="api-key-section">
      <div className="api-key-header">
        <div className="header-main">
          <Key size={20} />
          <h3>Gemini API Key</h3>
          {freeTierAvailable && (
            <span className="optional-badge">
              <Gift size={16} />
              Optional
            </span>
          )}
        </div>
        {freeTierAvailable && (
          <div className="free-tier-notice">
            <Zap size={16} />
            <span>Free tier available! {usageInfo?.remaining_today || 2} uses remaining today</span>
          </div>
        )}
      </div>
      
      <div className="api-key-input-container">
        <input
          type={showKey ? 'text' : 'password'}
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder={freeTierAvailable ? "Enter your API key for unlimited usage (optional)" : "Enter your Gemini API key..."}
          className="api-key-input"
        />
        <button
          type="button"
          onClick={() => setShowKey(!showKey)}
          className="toggle-visibility"
          aria-label={showKey ? 'Hide API key' : 'Show API key'}
        >
          {showKey ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>
      </div>
      
      <div className="api-key-help">
        {freeTierAvailable ? (
          <div className="pricing-tiers">
            <div className="tier free-tier">
              <Gift size={16} />
              <div className="tier-info">
                <strong>Free Tier</strong>
                <span>{usageInfo?.daily_limit || 2} uses per day • No setup required</span>
              </div>
            </div>
            <div className="tier unlimited-tier">
              <Zap size={16} />
              <div className="tier-info">
                <strong>Unlimited Tier</strong>
                <span>Your API key • No limits • 
                <a 
                  href="https://aistudio.google.com/app/apikey" 
                  target="_blank" 
                  rel="noopener noreferrer"
                >
                  Get Free Key
                </a>
                </span>
              </div>
            </div>
          </div>
        ) : (
          <p>
            Get your Gemini API key from{' '}
            <a 
              href="https://makersuite.google.com/app/apikey" 
              target="_blank" 
              rel="noopener noreferrer"
            >
              Google AI Studio
            </a>
          </p>
        )}
      </div>
    </div>
  );
};

export default ApiKeyInput; 