
import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [code, setCode] = useState("");
  const [review, setReview] = useState("");
  const [loading, setLoading] = useState(false);

  const handleReview = async () => {
    if (!code.trim()) {
      alert("Please enter code to review");
      return;
    }

    try {
      setLoading(true);
      setReview("");

      const response = await axios.post(
        "http://localhost:5000/review",
        {
          code: code,
        }
      );

      setReview(response.data.review);

    } catch (error) {
      console.error("Backend Error:", error);

      if (
        error.response &&
        error.response.data &&
        error.response.data.error
      ) {
        setReview(
          "❌ Backend Error: " +
          error.response.data.error
        );
      } else {
        setReview(
          "❌ Unable to connect to Flask backend."
        );
      }

    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setCode("");
    setReview("");
  };

  return (
    <div className="container">

      <h1 className="title">
        🤖 AI Code Reviewer
      </h1>

      <p className="subtitle">
        Analyze code quality, detect issues, and get AI-powered suggestions.
      </p>

      <textarea
        placeholder="Paste your code here..."
        value={code}
        onChange={(e) =>
          setCode(e.target.value)
        }
      />

      <div className="buttons">

        <button
          className="review-btn"
          onClick={handleReview}
          disabled={loading}
        >
          {loading
            ? "🔄 Reviewing..."
            : "🚀 Review Code"}
        </button>

        <button
          className="clear-btn"
          onClick={clearAll}
        >
          🗑️ Clear
        </button>

      </div>

      {review && (
        <div className="review-box">

          <h2>
            📋 Review Result
          </h2>

          <div className="review-content">
            {review}
          </div>

        </div>
      )}

    </div>
  );
}

export default App;