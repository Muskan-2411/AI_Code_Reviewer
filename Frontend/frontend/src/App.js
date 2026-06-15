import React, { useState } from "react";
import axios from "axios";
import "./App.css";

// API URL — set REACT_APP_API_URL in Railway environment variables
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

function App() {
  const [code, setCode] = useState("");
  const [review, setReview] = useState("");
  const [loading, setLoading] = useState(false);
  const [isError, setIsError] = useState(false);
  const [reviewTime, setReviewTime] = useState("");

  const handleReview = async () => {
    if (!code.trim()) {
      alert("Please paste some code to review.");
      return;
    }

    try {
      setLoading(true);
      setReview("");
      setIsError(false);

      const response = await axios.post(
        `${API_URL}/review`,
        { code: code },
        { timeout: 60000 }
      );

      setReview(response.data.review);
      setReviewTime(new Date().toLocaleTimeString());
    } catch (error) {
      console.error("Backend Error:", error);
      setIsError(true);

      if (error.response && error.response.data && error.response.data.error) {
        setReview("Error: " + error.response.data.error);
      } else if (error.code === "ECONNABORTED") {
        setReview(
          "Request timed out. The server may be starting up — please try again in a moment."
        );
      } else {
        setReview(
          "Unable to connect to the backend. Please check that the server is running."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setCode("");
    setReview("");
    setIsError(false);
    setReviewTime("");
  };

  const handleKeyDown = (e) => {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      handleReview();
    }
    // Tab key inserts spaces instead of moving focus
    if (e.key === "Tab") {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newCode = code.substring(0, start) + "  " + code.substring(end);
      setCode(newCode);
      // Set cursor position after the inserted spaces
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 2;
      }, 0);
    }
  };

  return (
    <div className="app-wrapper">
      {/* Background Effects */}
      <div className="bg-grid" />
      <div className="bg-orb bg-orb-1" />
      <div className="bg-orb bg-orb-2" />
      <div className="bg-orb bg-orb-3" />

      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="header-badge">
            <span className="pulse-dot"></span>
            AI-Powered Analysis
          </div>
          <h1 className="title">Code Reviewer</h1>
          <p className="subtitle">
            Paste your code below and get instant AI-powered feedback on quality,
            security, performance, and best practices.
          </p>
        </header>

        {/* Code Editor */}
        <div className="editor-card" id="code-editor">
          <div className="editor-toolbar">
            <div className="editor-dots">
              <span className="editor-dot red"></span>
              <span className="editor-dot yellow"></span>
              <span className="editor-dot green"></span>
            </div>
            <span className="editor-filename">your-code.js</span>
            <span className="editor-lang">
              {code.length > 0 ? `${code.split("\n").length} lines` : "empty"}
            </span>
          </div>
          <textarea
            id="code-input"
            placeholder={"// Paste your code here...\n// Press Ctrl + Enter to review\n\nfunction example() {\n  return 'Hello, World!';\n}"}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            onKeyDown={handleKeyDown}
            spellCheck={false}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
          />
        </div>

        {/* Action Buttons */}
        <div className="action-bar">
          <button
            id="review-btn"
            className="btn btn-primary"
            onClick={handleReview}
            disabled={loading || !code.trim()}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>🚀 Review Code</>
            )}
          </button>

          <button
            id="clear-btn"
            className="btn btn-secondary"
            onClick={clearAll}
            disabled={loading}
          >
            ✕ Clear
          </button>
        </div>

        {/* Status Bar */}
        {!loading && !review && (
          <div className="status-bar">
            <span className="status-dot"></span>
            Ready — powered by Groq &amp; LLaMA 3.3
          </div>
        )}

        {loading && (
          <div className="status-bar">
            <span className="status-dot"></span>
            Analyzing your code with AI...
          </div>
        )}

        {/* Review Result */}
        {review && (
          <div
            className={`review-card ${isError ? "error-state" : ""}`}
            id="review-result"
          >
            <div className="review-header">
              <div className="review-header-left">
                <div className="review-icon">
                  {isError ? "⚠️" : "✨"}
                </div>
                <span className="review-title">
                  {isError ? "Error" : "Review Result"}
                </span>
              </div>
              {reviewTime && (
                <span className="review-timestamp">{reviewTime}</span>
              )}
            </div>
            <div className="review-body">{review}</div>
          </div>
        )}

        {/* Footer */}
        <footer className="footer">
          Built with Flask, React &amp; Groq AI — Deployed on{" "}
          <a
            href="https://railway.app"
            target="_blank"
            rel="noopener noreferrer"
          >
            Railway
          </a>
        </footer>
      </div>
    </div>
  );
}

export default App;