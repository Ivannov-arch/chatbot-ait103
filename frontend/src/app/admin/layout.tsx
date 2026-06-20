"use client";

import React, { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";

/* ──────────────────────────────────────────
   Inline SVG icon helpers
────────────────────────────────────────── */
function IconDashboard() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
        d="M3 9.75L12 3l9 6.75V21a.75.75 0 01-.75.75H15a.75.75 0 01-.75-.75v-5.25h-4.5V21a.75.75 0 01-.75.75H3.75A.75.75 0 013 21V9.75z" />
    </svg>
  );
}

function IconBook() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
        d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  );
}

function IconChat() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );
}

function IconExternal() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
    </svg>
  );
}

function IconLogout() {
  return (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8}
        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
    </svg>
  );
}

/* ──────────────────────────────────────────
   Page title map
────────────────────────────────────────── */
function getPageTitle(pathname: string): string {
  if (pathname === "/admin") return "Dashboard Overview";
  if (pathname.startsWith("/admin/knowledge")) return "Knowledge Base";
  if (pathname.startsWith("/admin/logs")) return "Conversation Logs";
  return "Admin Portal";
}

/* ──────────────────────────────────────────
   Nav Item
────────────────────────────────────────── */
interface NavItemProps {
  href: string;
  label: string;
  icon: React.ReactNode;
  active: boolean;
  external?: boolean;
}

function NavItem({ href, label, icon, active, external }: NavItemProps) {
  const base =
    "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 cursor-pointer select-none";
  const activeClass = "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40";
  const inactiveClass =
    "text-slate-400 hover:text-white hover:bg-white/5";

  return (
    <Link
      href={href}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
      className={`${base} ${active ? activeClass : inactiveClass}`}
    >
      <span className="flex-shrink-0">{icon}</span>
      <span className="truncate">{label}</span>
      {external && (
        <span className="ml-auto text-slate-500">
          <IconExternal />
        </span>
      )}
    </Link>
  );
}

/* ──────────────────────────────────────────
   Main Layout
────────────────────────────────────────── */
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  const isLoginPage = pathname === "/admin/login";

  useEffect(() => {
    function checkAuth() {
      const isLoggedIn = localStorage.getItem("admin_logged_in");
      const email = localStorage.getItem("admin_email");

      if (isLoggedIn !== "true") {
        if (!isLoginPage) {
          router.push("/admin/login");
        } else {
          setLoading(false);
        }
      } else {
        setUserEmail(email || "admin@xmum.edu.my");
        if (isLoginPage) {
          router.push("/admin");
        } else {
          setLoading(false);
        }
      }
    }

    checkAuth();

    const handleStorageChange = () => checkAuth();
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, [router, isLoginPage]);

  const handleLogout = () => {
    localStorage.removeItem("admin_logged_in");
    localStorage.removeItem("admin_email");
    setUserEmail(null);
    router.push("/admin/login");
  };

  /* Loading screen */
  if (loading) {
    return (
      <div
        style={{ position: "fixed", inset: 0, display: "flex" }}
        className="flex-col items-center justify-center bg-slate-950 z-[99999]"
      >
        <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center mb-6 shadow-xl shadow-indigo-900/50">
          <span className="text-white font-black text-sm">XMU</span>
        </div>
        <svg className="animate-spin h-6 w-6 text-indigo-400 mb-3" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span className="text-slate-400 text-xs font-medium tracking-widest uppercase">Verifying session…</span>
      </div>
    );
  }

  /* Login page wrapper — full-screen gradient, no sidebar */
  if (isLoginPage) {
    return (
      <div
        style={{ position: "fixed", inset: 0, display: "flex" }}
        className="items-center justify-center bg-gradient-to-br from-slate-900 to-indigo-950 p-4 z-[9999]"
      >
        {children}
      </div>
    );
  }

  const isActive = (path: string) => {
    if (path === "/admin") return pathname === "/admin";
    return pathname.startsWith(path);
  };

  const initials = userEmail ? userEmail.substring(0, 2).toUpperCase() : "AD";
  const pageTitle = getPageTitle(pathname);

  return (
    <div
      style={{ position: "fixed", inset: 0, display: "flex" }}
      className="flex-row bg-slate-100 z-[9999] overflow-hidden"
    >
      {/* ── Sidebar ── */}
      <aside
        className="flex flex-col justify-between flex-shrink-0 overflow-hidden"
        style={{
          width: 256,
          background: "#0f172a",
          borderRight: "1px solid rgba(255,255,255,0.05)",
        }}
      >
        {/* Subtle top gradient overlay */}
        <div className="relative">
          <div
            className="absolute inset-x-0 top-0 h-32 pointer-events-none"
            style={{
              background:
                "linear-gradient(180deg, rgba(99,102,241,0.15) 0%, transparent 100%)",
            }}
          />

          {/* Logo */}
          <div className="relative flex items-center gap-3 px-5 py-5 border-b border-white/5">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-900/60 flex-shrink-0">
              <span className="text-white font-black text-xs tracking-tight">XMU</span>
            </div>
            <div className="min-w-0">
              <p className="text-white font-bold text-sm leading-tight truncate">XMUM CMS</p>
              <p className="text-indigo-400 text-[10px] font-semibold uppercase tracking-widest">
                Admin Portal
              </p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="relative px-3 pt-4 space-y-1">
            <NavItem
              href="/admin"
              label="Dashboard"
              icon={<IconDashboard />}
              active={isActive("/admin") && pathname === "/admin"}
            />
            <NavItem
              href="/admin/knowledge"
              label="Knowledge Base"
              icon={<IconBook />}
              active={isActive("/admin/knowledge")}
            />
            <NavItem
              href="/admin/logs"
              label="Conversation Logs"
              icon={<IconChat />}
              active={isActive("/admin/logs")}
            />

            {/* Separator */}
            <div className="h-px bg-white/5 my-3" />

            <NavItem
              href="/"
              label="Open Chat"
              icon={<IconExternal />}
              active={false}
              external
            />
          </nav>
        </div>

        {/* User section */}
        <div className="px-3 py-4 border-t border-white/5">
          <div className="flex items-center gap-3 px-3 py-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center font-bold text-xs text-white flex-shrink-0 shadow">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-white text-xs font-semibold truncate leading-tight">
                {userEmail}
              </p>
              <p className="text-slate-500 text-[10px] font-medium uppercase tracking-wider">
                Administrator
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-red-600/15 hover:bg-red-600 text-red-400 hover:text-white text-xs font-semibold rounded-xl transition-all duration-150 cursor-pointer border border-red-600/20 hover:border-red-600"
          >
            <IconLogout />
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── Main area ── */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-14 bg-black border-b border-slate-900 flex items-center justify-between px-6 flex-shrink-0 shadow-sm">
          <h1 className="text-slate-300 font-bold text-base tracking-tight">{pageTitle}</h1>
          <div className="flex items-center gap-2 bg-green-950 border border-green-500 px-3 py-1.5 rounded-full">
            <span className="w-2 h-2 rounded-full bg-green-300 flex-shrink-0" />
            <span className="text-green-300 text-xs font-semibold">Real Data Mode</span>
          </div>
        </header>

        {/* Scrollable content */}
        <div className="flex-1 overflow-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
