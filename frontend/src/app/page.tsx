"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabaseClient";

// ─── Admin whitelist ────────────────────────────────────────────────────────
const ADMIN_EMAILS = ["admin@xmum.edu.my", "dev@xmum.edu.my"];

// ─── Types ───────────────────────────────────────────────────────────────────
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

// ─── Suggested topics shown as chips ─────────────────────────────────────────
const FALLBACK_SUGGESTIONS = [
  "Library opening hours",
  "How to connect to WiFi",
  "Hostel application",
  "Scholarship requirements",
  "Cafeteria menu",
  "Bus schedule",
];

const SESSION_STORAGE_KEY = "xmum-chat-session-id";

function getBrowserSessionId() {
  if (typeof window === "undefined") return "browser-default";

  const existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
  if (existing) return existing;

  const sessionId = `web-${crypto.randomUUID()}`;
  window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
  return sessionId;
}

export default function ChatbotHome() {
  const [apiBaseUrl]                    = useState(() => process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
  const [apiStatus, setApiStatus]       = useState<"connecting" | "connected" | "error">("connecting");
  const [apiStatusMsg, setApiStatusMsg] = useState("Connecting to backend...");
  const [messages, setMessages]         = useState<Message[]>([]);
  const [suggestions, setSuggestions]   = useState<string[]>([]);
  const [inputVal, setInputVal]         = useState("");
  const [isLoading, setIsLoading]       = useState(false);

  // Debug — hidden from regular users, shown only to admins (Supabase session check)
  const [isAdmin, setIsAdmin]           = useState(false);
  const [showDebug, setShowDebug]       = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef       = useRef<HTMLInputElement>(null);
  const sessionIdRef   = useRef<string>("browser-default");

  // ── Check Supabase admin session ─────────────────────────────────────────
  useEffect(() => {
    async function checkAdmin() {
      const { data } = await supabase.auth.getSession();
      const email = data?.session?.user?.email;
      if (email && ADMIN_EMAILS.includes(email)) {
        setIsAdmin(true);
      }
    }
    checkAdmin();
  }, []);

  // ── Resolve browser session ───────────────────────────────────────────────
  useEffect(() => {
    sessionIdRef.current = getBrowserSessionId();
  }, []);

  // ── Health check + greeting + suggestions ─────────────────────────────────
  useEffect(() => {
    if (!apiBaseUrl) return;
    let alive = true;

    async function init() {
      // Health check with path fallback
      let ok = false;
      for (const path of ["/api/health", "/health"]) {
        try {
          const r = await fetch(`${apiBaseUrl}${path}`);
          if (r.ok) { ok = true; break; }
        } catch { /* try next */ }
      }

      if (!alive) return;

      if (ok) {
        setApiStatus("connected");
        setApiStatusMsg("✓ Connected");
        setTimeout(() => alive && setApiStatusMsg(""), 3000);

        // Fetch suggestions
        for (const path of ["/api/suggestions?limit=8", "/suggestions?limit=8"]) {
          try {
            const r = await fetch(`${apiBaseUrl}${path}`);
            if (r.ok) {
              const d = await r.json();
              if (alive) setSuggestions(d.suggestions || []);
              break;
            }
          } catch { /* try next */ }
        }
      } else {
        setApiStatus("error");
        setApiStatusMsg("Backend offline — using fallback suggestions");
        setSuggestions(FALLBACK_SUGGESTIONS);
      }
    }

    // Greeting
    const t = setTimeout(() => {
      if (alive) {
        setMessages([{
          id: "greeting",
          role: "bot",
          text: "Hi there! 👋 I'm <strong>XMUM Campus Assistant</strong>.<br/>Ask me anything — library, hostel, WiFi, scholarships, food, transport, and more!",
        }]);
      }
    }, 250);

    init();
    return () => { alive = false; clearTimeout(t); };
  }, [apiBaseUrl]);

  // ── Auto-scroll ───────────────────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // ── Send message ──────────────────────────────────────────────────────────
  const handleSend = async (override?: string) => {
    const text = (override ?? inputVal).trim();
    if (!text || isLoading) return;

    setMessages(prev => [...prev, { id: `u-${Date.now()}`, role: "user", text }]);
    setInputVal("");
    setIsLoading(true);
    inputRef.current?.focus();

    let answer = "Sorry, there was an error communicating with the backend.";
    let hasError = false;
    let debug: DebugData | undefined;

    try {
      const payload = {
        message: text,
        session_id: sessionIdRef.current,
        debug: showDebug,
      };
      let response: Response | undefined;

      for (const path of ["/api/chat", "/chat"]) {
        try {
          response = await fetch(`${apiBaseUrl}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (response.ok || response.status !== 404) break;
        } catch { /* try next */ }
      }

      if (response?.ok) {
        const d = await response.json();
        answer = d.answer || "No response received.";
        debug = {
          matched_question: d.matched_question,
          confidence: d.confidence,
          module: d.module,
          sub_intent: d.sub_intent,
          entities: d.entities,
        };
      } else {
        hasError = true;
        answer = apiStatus !== "connected"
          ? "Backend is not connected. Please start the Python server."
          : `Backend error (HTTP ${response?.status ?? "?"}).`;
      }
    } catch {
      hasError = true;
      answer = "Failed to reach the backend. Is the server running?";
    }

    setMessages(prev => [...prev, {
      id: `b-${Date.now()}`, role: "bot", text: answer, error: hasError, debugData: debug,
    }]);
    setIsLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSend();
  };

  // ── Status dot colour ─────────────────────────────────────────────────────
  const statusDot = {
    connecting: "bg-amber-400 animate-pulse",
    connected:  "bg-emerald-400",
    error:      "bg-red-500",
  }[apiStatus];

  return (
    <div className="chat-shell">

      {/* ── Header ── */}
      <header className="chat-header">
        <div className="chat-header-brand">
          <div className="brand-avatar">XMU</div>
          <div>
            <p className="brand-name">XMUM Campus Assistant</p>
            <p className="brand-sub">NLP-Powered · Python Backend</p>
          </div>
        </div>

        <div className="chat-header-actions">
          {/* Connection status */}
          <span className="status-chip">
            <span className={`status-dot ${statusDot}`} />
            {apiStatusMsg || (apiStatus === "connected" ? "Online" : "Connecting…")}
          </span>

          {/* Debug toggle — only rendered if admin session detected */}
          {isAdmin && (
            <button
              onClick={() => setShowDebug(v => !v)}
              className={`pill-btn ${showDebug ? "pill-btn--active" : ""}`}
              title="Admin-only debug toggle"
            >
              🛠 Debug {showDebug ? "On" : "Off"}
            </button>
          )}

          <Link href="/admin/login" className="pill-btn pill-btn--primary">
            Admin CMS →
          </Link>
        </div>
      </header>

      {/* ── Suggestion chips ── */}
      {suggestions.length > 0 && (
        <div className="chip-bar">
          <span className="chip-label">Try asking:</span>
          <div className="chip-list">
            {suggestions.map((s, i) => (
              <button
                key={i}
                className="chip"
                disabled={isLoading}
                onClick={() => handleSend(s)}
              >
                {s.length > 42 ? `${s.slice(0, 42)}…` : s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Messages ── */}
      <div className="messages-pane" id="msgs">
        {messages.map(msg => (
          <div key={msg.id} className={`msg-row msg-row--${msg.role}`}>

            <div className={`msg-avatar ${msg.role === "user" ? "msg-avatar--user" : ""}`}>
              {msg.role === "user" ? "U" : "🤖"}
            </div>

            <div className={`bubble ${msg.role === "user" ? "bubble--user" : "bubble--bot"} ${msg.error ? "bubble--error" : ""}`}>
              <div dangerouslySetInnerHTML={{ __html: msg.text }} />

              {/* Debug panel (admin only) */}
              {isAdmin && showDebug && msg.debugData && msg.role === "bot" && !msg.error && (
                <div className="debug-panel">
                  <p className="debug-title">🛠 Debug Info</p>
                  {msg.debugData.matched_question && (
                    <div className="debug-row">
                      <span className="debug-key">Best match</span>
                      <span className="debug-val">&quot;{msg.debugData.matched_question}&quot;</span>
                    </div>
                  )}
                  {msg.debugData.confidence !== undefined && (
                    <div className="debug-row">
                      <span className="debug-key">Confidence</span>
                      <span className="debug-val">{(msg.debugData.confidence * 100).toFixed(1)}%</span>
                    </div>
                  )}
                  {msg.debugData.module && (
                    <div className="debug-row">
                      <span className="debug-key">Module</span>
                      <span className="debug-val">{msg.debugData.module}</span>
                    </div>
                  )}
                  {msg.debugData.sub_intent && (
                    <div className="debug-row">
                      <span className="debug-key">Intent</span>
                      <span className="debug-val">{msg.debugData.sub_intent}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className="msg-row msg-row--bot">
            <div className="msg-avatar">🤖</div>
            <div className="bubble bubble--bot bubble--typing">
              <span /><span /><span />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Input ── */}
      <div className="input-bar">
        <input
          ref={inputRef}
          id="inp"
          type="text"
          value={inputVal}
          onChange={e => setInputVal(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Ask me anything about XMUM campus…"
          autoComplete="off"
        />
        <button
          id="sendBtn"
          onClick={() => handleSend()}
          disabled={!inputVal.trim() || isLoading}
          aria-label="Send message"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </div>
  );
}
