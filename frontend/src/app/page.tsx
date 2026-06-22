"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabaseClient";
import { getKnowledgeItems } from "@/services/knowledgeService";

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
  const [searchQuery, setSearchQuery] = useState("");

  // Mobile & Desktop sidebar states
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDesktopCollapsed, setIsDesktopCollapsed] = useState(false);

  // Debug — hidden from regular users, shown only to admins (Supabase session check)
  const [isAdmin, setIsAdmin] = useState(false);
  const [showDebug, setShowDebug] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch FAQs for sidebar
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
      if (email) {
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

  // Filter and group FAQs by module
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
    <div className="flex h-screen w-full overflow-hidden relative bg-slate-900">
      {/* Backdrop overlay — mobile only, closes sidebar on outside click */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 md:hidden transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar — Blue theme (bg-blue-950) & Dynamic width on large screens (lg) */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 bg-blue-950 border-r border-blue-900/50 flex flex-col h-full transform transition-all duration-300 ease-in-out shrink-0 text-white
          ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0 
          ${isDesktopCollapsed ? "md:w-16" : "md:w-80"}`}
      >
        <div className="p-4 border-b border-blue-900/40 flex flex-col gap-3">
          <div className="flex items-center justify-between">
            {/* Only show text if not collapsed */}
            {!isDesktopCollapsed ? (
              <div>
                <h2 className="text-base font-bold text-blue-200 flex items-center gap-2">
                  <span>📚</span> Campus FAQ
                </h2>
                <p className="text-xs text-blue-400 mt-0.5">
                  Click to ask the bot directly
                </p>
              </div>
            ) : (
              <div
                className="hidden md:flex mx-auto text-xl"
                title="Campus FAQ"
              >
                📚
              </div>
            )}

            <div className="flex items-center gap-1">
              {/* Toggle Hide/Show button for Desktop */}
              <button
                onClick={() => setIsDesktopCollapsed(!isDesktopCollapsed)}
                className="hidden md:block text-blue-300 hover:text-white hover:bg-blue-900/50 p-1.5 rounded-lg text-sm transition-colors border border-blue-800"
                title={
                  isDesktopCollapsed ? "Expand Sidebar" : "Collapse Sidebar"
                }
              >
                {isDesktopCollapsed ? "→" : "←"}
              </button>

              {/* Close button — mobile only */}
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="md:hidden text-blue-300 hover:text-white p-1 rounded-lg text-lg"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Search Keyword — Hide completely if collapsed on large screens */}
          <div
            className={`relative ${isDesktopCollapsed ? "md:hidden" : "block"}`}
          >
            <input
              type="text"
              placeholder="Search questions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full text-sm pl-8 pr-3 py-1.5 bg-blue-900/40 border border-blue-800 rounded-lg focus:outline-none focus:border-blue-400 focus:bg-blue-900/60 text-white transition-all placeholder-blue-300/60"
            />
            <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-blue-300 pointer-events-none text-xs">
              🔍
            </span>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery("")}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-blue-300 hover:text-white text-xs"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* FAQ List Content — Hide menu contents when collapsed */}
        <div
          className={`flex-1 overflow-y-auto p-4 space-y-6 select-none ${isDesktopCollapsed ? "md:hidden" : "block"}`}
        >
          {Object.keys(groupedFaqs).length === 0 ? (
            <p className="text-sm text-blue-300/60 text-center py-4">
              {faqs.length === 0
                ? "Loading FAQs..."
                : "No matching questions found."}
            </p>
          ) : (
            Object.entries(groupedFaqs).map(([moduleName, items]) => (
              <div key={moduleName} className="space-y-2">
                <h3 className="text-xs font-bold text-blue-300 uppercase tracking-wider px-1">
                  {moduleName}
                </h3>
                <div className="space-y-1">
                  {items.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        handleSend(item.question);
                        setIsSidebarOpen(false);
                      }}
                      disabled={isLoading}
                      className="w-full text-left text-sm text-slate-200 hover:text-white hover:bg-blue-900/50 px-3 py-2 rounded-lg transition-all duration-200 block truncate"
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

        {/* Vertical mini indicator when sidebar is collapsed */}
        {isDesktopCollapsed && (
          <div
            className="hidden md:flex flex-1 flex-col items-center pt-6 space-y-4 text-blue-400 text-sm cursor-pointer"
            onClick={() => setIsDesktopCollapsed(false)}
          >
            <span className="writing-mode-vertical tracking-widest font-bold uppercase opacity-40 ">
              FAQ PANEL
            </span>
          </div>
        )}
      </aside>

      {/* ── CHAT CONTAINER MAIN ── */}
      <main className="flex-1 flex justify-center items-center p-4 lg:p-6 h-full overflow-hidden">
        <div className="chat-shell w-full max-w-4xl h-full flex flex-col overflow-hidden">
          {/* ── Header ── */}
          <header className="chat-header">
            <div className="chat-header-brand flex items-center gap-2">
              {/* Hamburger button — mobile or when desktop is collapsed */}
              <button
                onClick={() => {
                  if (window.innerWidth < 768) {
                    setIsSidebarOpen(true);
                  } else {
                    setIsDesktopCollapsed(false);
                  }
                }}
                className={`${isDesktopCollapsed ? "md:flex" : "md:hidden"} flex items-center justify-center p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors mr-1`}
                aria-label="Open FAQ Menu"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>

              <div className="brand-avatar">XMU</div>
              <div>
                <p className="brand-name">XMUM Campus Assistant</p>
                <p className="brand-sub">NLP-Powered · Python Backend</p>
              </div>
            </div>

            <div className="chat-header-actions">
              <span className="status-chip">
                <span className={`status-dot ${statusDot}`} />
                <span className="hidden sm:inline">
                  {apiStatusMsg ||
                    (apiStatus === "connected" ? "Online" : "Connecting…")}
                </span>
              </span>

              {isAdmin && (
                <button
                  onClick={() => setShowDebug((v) => !v)}
                  className={`pill-btn ${showDebug ? "pill-btn--active" : ""}`}
                  title="Admin-only debug toggle"
                >
                  🛠{" "}
                  <span className="hidden sm:inline">
                    Debug {showDebug ? "On" : "Off"}
                  </span>
                </button>
              )}

              <Link href="/admin/login" className="pill-btn pill-btn--primary">
                Admin <span className="hidden sm:inline">CMS</span> →
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
