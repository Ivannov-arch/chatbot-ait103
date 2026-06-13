"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";

interface DebugData {
  matched_question?: string;
  confidence?: number;
  module?: string;
  sub_intent?: string;
  entities?: string[];
}

interface Message {
  id: string;
  role: "user" | "bot";
  text: string;
  error?: boolean;
  debugData?: DebugData;
}

export default function ChatbotHome() {
  const [apiBaseUrl, setApiBaseUrl] = useState<string>("");
  const [apiStatus, setApiStatus] = useState<"connecting" | "connected" | "error">("connecting");
  const [apiStatusMessage, setApiStatusMessage] = useState<string>("Connecting to backend...");
  const [messages, setMessages] = useState<Message[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [inputVal, setInputVal] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showDebug, setShowDebug] = useState<boolean>(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Setup API URL on client side
  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    setApiBaseUrl(url);
  }, []);

  // Initialize and check health
  useEffect(() => {
    if (!apiBaseUrl) return;

    let isMounted = true;

    async function initialize() {
      // 1. Health check with fallback paths
      let connected = false;
      let checkUrl = `${apiBaseUrl}/api/health`;

      try {
        let response = await fetch(checkUrl);
        if (response.ok) {
          connected = true;
        } else {
          checkUrl = `${apiBaseUrl}/health`;
          response = await fetch(checkUrl);
          if (response.ok) {
            connected = true;
          }
        }
      } catch (err) {
        try {
          checkUrl = `${apiBaseUrl}/health`;
          const response = await fetch(checkUrl);
          if (response.ok) {
            connected = true;
          }
        } catch (e) {
          connected = false;
        }
      }

      if (!isMounted) return;

      if (connected) {
        setApiStatus("connected");
        setApiStatusMessage("✓ Connected to backend");
        
        // Hide status bar after 3 seconds
        setTimeout(() => {
          if (isMounted) {
            setApiStatusMessage("");
          }
        }, 3000);

        // 2. Fetch suggestions with fallback paths
        try {
          let sugUrl = `${apiBaseUrl}/api/suggestions?limit=10`;
          let res = await fetch(sugUrl);
          if (!res.ok) {
            sugUrl = `${apiBaseUrl}/suggestions?limit=10`;
            res = await fetch(sugUrl);
          }
          if (res.ok) {
            const data = await res.json();
            if (isMounted) {
              setSuggestions(data.suggestions || []);
            }
          }
        } catch (sugErr) {
          console.error("Failed to load suggestions:", sugErr);
        }
      } else {
        setApiStatus("error");
        setApiStatusMessage(`✗ Backend not running on ${apiBaseUrl}`);
      }
    }

    initialize();

    // Greeting message
    const greetingTimeout = setTimeout(() => {
      if (isMounted) {
        setMessages([
          {
            id: "greeting",
            role: "bot",
            text: "Hello! I'm the XMUM Campus Assistant 👋<br>Ask me anything about campus life, library, hostel, scholarships, WiFi, food, transport, and more!",
          },
        ]);
      }
    }, 300);

    return () => {
      isMounted = false;
      clearTimeout(greetingTimeout);
    };
  }, [apiBaseUrl]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  // Handle sending message
  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputVal).trim();
    if (!text || isLoading) return;

    const userMsgId = `user-${Date.now()}`;
    setMessages((prev) => [...prev, { id: userMsgId, role: "user", text: text }]);
    setInputVal("");
    setIsLoading(true);

    let answer = "Sorry, there was an error communicating with the backend.";
    let errorOccurred = false;
    let debug: DebugData | undefined;

    try {
      let chatUrl = `${apiBaseUrl}/api/chat`;
      let payload = { message: text, debug: showDebug };
      
      let response;
      try {
        response = await fetch(chatUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      } catch (err) {
        chatUrl = `${apiBaseUrl}/chat`;
        response = await fetch(chatUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (!response.ok && response.status === 404 && chatUrl.includes("/api/chat")) {
        chatUrl = `${apiBaseUrl}/chat`;
        response = await fetch(chatUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }

      if (response && response.ok) {
        const data = await response.json();
        answer = data.answer || "No response received.";
        debug = {
          matched_question: data.matched_question,
          confidence: data.confidence,
          module: data.module,
          sub_intent: data.sub_intent,
          entities: data.entities,
        };
      } else {
        errorOccurred = true;
        answer = `Sorry, the backend returned an error (HTTP ${response?.status || "Unknown"}).`;
      }
    } catch (err) {
      console.error("Chat API Error:", err);
      errorOccurred = true;
      if (apiStatus !== "connected") {
        answer = "Sorry, the backend is not connected. Please make sure the Python server is running.";
      } else {
        answer = "Sorry, failed to connect to the chat API.";
      }
    }

    setMessages((prev) => [
      ...prev,
      {
        id: `bot-${Date.now()}`,
        role: "bot",
        text: answer,
        error: errorOccurred,
        debugData: debug,
      },
    ]);
    setIsLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  return (
    <div className="app">
      {/* API Status Bar */}
      {apiStatusMessage && (
        <div className={`api-status ${apiStatus}`}>
          {apiStatusMessage}
        </div>
      )}

      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <div className="avatar">XMU</div>
          <div>
            <div className="title">XMUM New Student Campus Assistant</div>
            <div className="sub">NLP-Powered Campus Assistant with Python Backend</div>
          </div>
        </div>
        
        {/* Actions (Toggle Debug & Admin Link) */}
        <div className="header-actions">
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="btn-outline"
          >
            {showDebug ? "Debug: On" : "Debug: Off"}
          </button>
          <Link href="/admin/login" className="btn-primary">
            Admin CMS
          </Link>
        </div>
      </div>

      {/* Suggestions Chips */}
      {suggestions.length > 0 && (
        <div className="suggestions">
          <div className="sug-label">Quick questions:</div>
          {suggestions.map((sug, idx) => (
            <button
              key={idx}
              className="sug-btn"
              onClick={() => handleSend(sug)}
              disabled={isLoading}
            >
              {sug.length > 40 ? `${sug.substring(0, 40)}...` : sug}
            </button>
          ))}
        </div>
      )}

      {/* Messages Window */}
      <div className="messages" id="msgs">
        {messages.map((msg) => (
          <div key={msg.id} className={`msg ${msg.role}`}>
            <div className="mini-av">
              {msg.role === "user" ? "👤" : "🤖"}
            </div>
            <div className="bubble">
              <div dangerouslySetInnerHTML={{ __html: msg.text }} />

              {/* Render debug info if active and provided */}
              {showDebug && msg.debugData && msg.role === "bot" && !msg.error && (
                <>
                  {msg.debugData.matched_question && (
                    <div className="debug-pill">
                      <b>Best match:</b> &ldquo;{msg.debugData.matched_question}&rdquo; 
                      {msg.debugData.confidence !== undefined && (
                        <> — confidence {(msg.debugData.confidence * 100).toFixed(0)}%</>
                      )}
                    </div>
                  )}
                  {(msg.debugData.module || msg.debugData.sub_intent) && (
                    <div className="debug-pill">
                      {msg.debugData.module && `module: ${msg.debugData.module}`}
                      {msg.debugData.sub_intent && ` | intent: ${msg.debugData.sub_intent}`}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="msg bot" id="loadingMsg">
            <div className="mini-av">🤖</div>
            <div className="bubble loading">
              Thinking
              <span className="dots-container">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input row */}
      <div className="input-row">
        <input
          id="inp"
          type="text"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Ask about campus (e.g. library hours, scholarship, hostel...)"
        />
        <button
          id="sendBtn"
          onClick={() => handleSend()}
          disabled={!inputVal.trim() || isLoading}
        >
          Send ➜
        </button>
      </div>
    </div>
  );
}
