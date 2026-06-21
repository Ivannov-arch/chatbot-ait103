"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabaseClient";
import { getKnowledgeItems } from "@/services/knowledgeService";

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

interface FAQItem {
  id: string;
  module: string;
  question: string;
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

export default function ChatbotHome() {
  const [apiBaseUrl, setApiBaseUrl] = useState("");
  const [apiStatus, setApiStatus] = useState<
    "connecting" | "connected" | "error"
  >("connecting");
  const [apiStatusMsg, setApiStatusMsg] = useState("Connecting to backend...");
  const [messages, setMessages] = useState<Message[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [inputVal, setInputVal] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // FAQ Sidebar State & Search State
  const [faqs, setFaqs] = useState<FAQItem[]>([]);
  const [searchQuery, setSearchQuery] = useState(""); // 1. STATE BARU UNTUK PENCARIAN

  // Debug — hidden from regular users, shown only to admins (Supabase session check)
  const [isAdmin, setIsAdmin] = useState(false);
  const [showDebug, setShowDebug] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // ── Fetch FAQs untuk Sidebar ──────────────────────────────────────────────
  useEffect(() => {
    async function loadFAQs() {
      try {
        const data = await getKnowledgeItems();
        if (data) {
          setFaqs(data as FAQItem[]);
        }
      } catch (error) {
        console.error("Error fetching FAQs for sidebar:", error);
      }
    }
    loadFAQs();
  }, []);

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

  // ── Resolve API base URL ──────────────────────────────────────────────────
  useEffect(() => {
    setApiBaseUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
  }, []);

  // ── Health check + greeting + suggestions ─────────────────────────────────
  useEffect(() => {
    if (!apiBaseUrl) return;
    let alive = true;

    async function init() {
      let ok = false;
      for (const path of ["/api/health", "/health"]) {
        try {
          const r = await fetch(`${apiBaseUrl}${path}`);
          if (r.ok) {
            ok = true;
            break;
          }
        } catch {
          /* try next */
        }
      }

      if (!alive) return;

      if (ok) {
        setApiStatus("connected");
        setApiStatusMsg("✓ Connected");
        setTimeout(() => alive && setApiStatusMsg(""), 3000);

        for (const path of [
          "/api/suggestions?limit=8",
          "/suggestions?limit=8",
        ]) {
          try {
            const r = await fetch(`${apiBaseUrl}${path}`);
            if (r.ok) {
              const d = await r.json();
              if (alive) setSuggestions(d.suggestions || []);
              break;
            }
          } catch {
            /* try next */
          }
        }
      } else {
        setApiStatus("error");
        setApiStatusMsg("Backend offline — using fallback suggestions");
        setSuggestions(FALLBACK_SUGGESTIONS);
      }
    }

    const t = setTimeout(() => {
      if (alive) {
        setMessages([
          {
            id: "greeting",
            role: "bot",
            text: "Hi there! 👋 I'm <strong>XMUM Campus Assistant</strong>.<br/>Ask me anything — library, hostel, WiFi, scholarships, food, transport, and more!",
          },
        ]);
      }
    }, 250);

    init();
    return () => {
      alive = false;
      clearTimeout(t);
    };
  }, [apiBaseUrl]);

  // ── Auto-scroll ───────────────────────────────────────────────────────────
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // ── Send message ──────────────────────────────────────────────────────────
  const handleSend = async (override?: string) => {
    const text = (override ?? inputVal).trim();
    if (!text || isLoading) return;

    setMessages((prev) => [
      ...prev,
      { id: `u-${Date.now()}`, role: "user", text },
    ]);
    setInputVal("");
    setIsLoading(true);
    inputRef.current?.focus();

    let answer = "Sorry, there was an error communicating with the backend.";
    let hasError = false;
    let debug: DebugData | undefined;

    try {
      const payload = { message: text, debug: showDebug };
      let response: Response | undefined;

      for (const path of ["/api/chat", "/chat"]) {
        try {
          response = await fetch(`${apiBaseUrl}${path}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          if (response.ok || response.status !== 404) break;
        } catch {
          /* try next */
        }
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
        answer =
          apiStatus !== "connected"
            ? "Backend is not connected. Please start the Python server."
            : `Backend error (HTTP ${response?.status ?? "?"}).`;
      }
    } catch {
      hasError = true;
      answer = "Failed to reach the backend. Is the server running?";
    }

    setMessages((prev) => [
      ...prev,
      {
        id: `b-${Date.now()}`,
        role: "bot",
        text: answer,
        error: hasError,
        debugData: debug,
      },
    ]);
    setIsLoading(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSend();
  };

  // 2. LOGIKA FILTER & GROUPING BERDASARKAN KATA KUNCI
  const filteredFaqs = faqs.filter((item) => {
    const query = searchQuery.toLowerCase();
    return (
      item.question.toLowerCase().includes(query) ||
      (item.module && item.module.toLowerCase().includes(query))
    );
  });

  const groupedFaqs = filteredFaqs.reduce(
    (acc, item) => {
      const moduleName = item.module || "General";
      if (!acc[moduleName]) {
        acc[moduleName] = [];
      }
      acc[moduleName].push(item);
      return acc;
    },
    {} as Record<string, FAQItem[]>,
  );

  const statusDot = {
    connecting: "bg-amber-400 animate-pulse",
    connected: "bg-emerald-400",
    error: "bg-red-500",
  }[apiStatus];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* ── SIDEBAR FAQ (Kiri) ── */}
      <aside className="w-80 bg-white border-r border-gray-200 flex flex-col h-full hidden md:flex shrink-0">
        <div className="p-4 border-b border-gray-100 flex flex-col gap-3">
          <div>
            <h2 className="text-base font-bold text-gray-800 flex items-center gap-2">
              <span>📚</span> Campus Knowledge FAQ
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">
              Click any question to ask the bot directly
            </p>
          </div>

          {/* 3. INPUT BARU: SEARCH KEYWORD */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search questions or modules..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-sm pl-8 pr-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:bg-white text-gray-700 transition-all placeholder-gray-400"
            />
            {/* Icon Kaca Pembesar (Magnifying Glass) */}
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none text-xs">
              🔍
            </span>
            {/* Tombol Clear (X) jika input terisi */}
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 select-none">
          {Object.keys(groupedFaqs).length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-4">
              {faqs.length === 0
                ? "Loading FAQs..."
                : "No matching questions found."}
            </p>
          ) : (
            Object.entries(groupedFaqs).map(([moduleName, items]) => (
              <div key={moduleName} className="space-y-2">
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
                  {moduleName}
                </h3>
                <div className="space-y-1">
                  {items.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleSend(item.question)}
                      disabled={isLoading}
                      className="w-full text-left text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50/50 px-3 py-2 rounded-lg transition-all duration-200 block truncate"
                      title={item.question}
                    >
                      • {item.question}
                    </button>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* ── CHAT CONTAINER MAIN (Tengah Simetris) ── */}
      <main className="flex-1 flex justify-center items-center p-4 lg:p-6 h-full overflow-hidden">
        <div className="chat-shell w-full max-w-4xl h-full flex flex-col overflow-hidden">
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
              <span className="status-chip">
                <span className={`status-dot ${statusDot}`} />
                {apiStatusMsg ||
                  (apiStatus === "connected" ? "Online" : "Connecting…")}
              </span>

              {isAdmin && (
                <button
                  onClick={() => setShowDebug((v) => !v)}
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
            {messages.map((msg) => (
              <div key={msg.id} className={`msg-row msg-row--${msg.role}`}>
                <div
                  className={`msg-avatar ${msg.role === "user" ? "msg-avatar--user" : ""}`}
                >
                  {msg.role === "user" ? "U" : "🤖"}
                </div>

                <div
                  className={`bubble ${msg.role === "user" ? "bubble--user" : "bubble--bot"} ${msg.error ? "bubble--error" : ""}`}
                >
                  <div dangerouslySetInnerHTML={{ __html: msg.text }} />

                  {/* Debug panel (admin only) */}
                  {isAdmin &&
                    showDebug &&
                    msg.debugData &&
                    msg.role === "bot" &&
                    !msg.error && (
                      <div className="debug-panel">
                        <p className="debug-title">🛠 Debug Info</p>
                        {msg.debugData.matched_question && (
                          <div className="debug-row">
                            <span className="debug-key">Best match</span>
                            <span className="debug-val">
                              "{msg.debugData.matched_question}"
                            </span>
                          </div>
                        )}
                        {msg.debugData.confidence !== undefined && (
                          <div className="debug-row">
                            <span className="debug-key">Confidence</span>
                            <span className="debug-val">
                              {(msg.debugData.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                        {msg.debugData.module && (
                          <div className="debug-row">
                            <span className="debug-key">Module</span>
                            <span className="debug-val">
                              {msg.debugData.module}
                            </span>
                          </div>
                        )}
                        {msg.debugData.sub_intent && (
                          <div className="debug-row">
                            <span className="debug-key">Intent</span>
                            <span className="debug-val">
                              {msg.debugData.sub_intent}
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="msg-row msg-row--bot">
                <div className="msg-avatar">🤖</div>
                <div className="bubble bubble--bot bubble--typing">
                  <span />
                  <span />
                  <span />
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
              onChange={(e) => setInputVal(e.target.value)}
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
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
