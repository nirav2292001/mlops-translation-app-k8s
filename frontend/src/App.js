import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [translated, setTranslated] = useState('');
  const [loading, setLoading] = useState(false);
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('de');
  const [apiUrl, setApiUrl] = useState('http://localhost:8000'); // fallback

  // ⬇️ Load the API URL dynamically from env.js
  useEffect(() => {
    if (window.env && window.env.REACT_APP_API_URL) {
      setApiUrl(window.env.REACT_APP_API_URL);
    }
  }, []);

  const handleTranslate = async () => {
    if (!text.trim()) {
      alert('Please enter text to translate');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text,
          source_lang: sourceLang,
          target_lang: targetLang 
        }),
      });

      if (!response.ok) {
        throw new Error('Translation failed');
      }

      const data = await response.json();
      setTranslated(data.translated_text);
    } catch (error) {
      console.error(error);
      setTranslated('Translation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setTranslated('');
  };

  const handleCopy = () => {
    if (!translated) return;
    navigator.clipboard.writeText(translated);
    alert('Translated text copied to clipboard!');
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>AI TRANSLATOR test2  </h1>
        <div className="language-selectors">
          <select 
            value={sourceLang} 
            onChange={(e) => setSourceLang(e.target.value)}
            className="language-selector"
          >
            <option value="en">English</option>
            <option value="de">German</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
          </select>
          <span>→</span>
          <select 
            value={targetLang} 
            onChange={(e) => setTargetLang(e.target.value)}
            className="language-selector"
          >
            <option value="de">German</option>
            <option value="en">English</option>
            <option value="fr">French</option>
            <option value="es">Spanish</option>
          </select>
        </div>
      </div>

      <div className="translation-container">
        <div className="input-section">
          <textarea
            rows="6"
            placeholder="Enter text to translate..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="text-input"
          />
          <div className="button-group">
            <button 
              onClick={handleTranslate} 
              disabled={loading || !text.trim()}
              className="action-button translate-button"
            >
              {loading ? 'Translating...' : 'Translate'}
            </button>
            <button 
              onClick={handleClear} 
              disabled={!text.trim()}
              className="action-button clear-button"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="output-section">
          <h3>Translated Text:</h3>
          <div className="translated-text">
            {translated || 'No translation yet'}
          </div>
          <button 
            onClick={handleCopy} 
            disabled={!translated}
            className="action-button copy-button"
          >
            Copy to Clipboard
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
