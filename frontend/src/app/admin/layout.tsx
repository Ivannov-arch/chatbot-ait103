"use client";

import React, { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";

/* ──────────────────────────────────────────
   Inline SVG icon helpers (Tambahan Icon Menu & Close)
────────────────────────────────────────── */
function IconMenu() {
  return (
    <svg
      className="w-6 h-6"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 6h16M4 12h16M4 18h16"
      />
    </svg>
  );
}

function IconClose() {
  return (
    <svg
      className="w-6 h-6"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  );
}

function IconDashboard() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M3 9.75L12 3l9 6.75V21a.75.75 0 01-.75.75H15a.75.75 0 01-.75-.75v-5.25h-4.5V21a.75.75 0 01-.75.75H3.75A.75.75 0 013 21V9.75z"
      />
    </svg>
  );
}

function IconBook() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
      />
    </svg>
  );
}

function IconChat() {
  return (
    <svg
      className="w-5 h-5"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
      />
    </svg>
  );
}

function IconExternal() {
  return (
    <svg
      className="w-4 h-4"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
      />
    </svg>
  );
}

/* ──────────────────────────────────────────
   Helper Title & NavItem
────────────────────────────────────────── */
function getPageTitle(pathname: string): string {
  if (pathname === "/admin") return "Dashboard Overview";
  if (pathname.startsWith("/admin/knowledge")) return "Knowledge Base";
  if (pathname.startsWith("/admin/logs")) return "Conversation Logs";
  return "Admin Portal";
}

interface NavItemProps {
  href: string;
  label: string;
  icon: React.ReactNode;
  active: boolean;
  external?: boolean;
  onClick?: () => void;
}

function NavItem({
  href,
  label,
  icon,
  active,
  external,
  onClick,
}: NavItemProps) {
  return (
    <Link
      href={href}
      onClick={onClick}
      target={external ? "_blank" : undefined}
      rel={external ? "noopener noreferrer" : undefined}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 select-none ${
        active
          ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
          : "text-slate-400 hover:text-white hover:bg-white/5"
      }`}
    >
      <span className="flex-shrink-0">{icon}</span>
      <span className="truncate">{label}</span>
      {external && (
        <span className="ml-auto text-slate-500 flex-shrink-0">
          <IconExternal />
        </span>
      )}
    </Link>
  );
}

/* ──────────────────────────────────────────
   Main Layout Component
────────────────────────────────────────── */
export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false); // State kontrol menu HP

  const isLoginPage = pathname === "/admin/login";

  useEffect(() => {
    function checkAuth() {
      const isLoggedIn = localStorage.getItem("admin_logged_in");
      const email = localStorage.getItem("admin_email");

      if (isLoggedIn !== "true") {
        if (!isLoginPage) router.push("/admin/login");
        else setLoading(false);
      } else {
        setUserEmail(email || "admin@xmum.edu.my");
        if (isLoginPage) router.push("/admin");
        else setLoading(false);
      }
    }
    checkAuth();
  }, [router, isLoginPage]);

  // Tutup sidebar otomatis saat pindah rute di HP
  useEffect(() => {
    setMobileSidebarOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem("admin_logged_in");
    localStorage.removeItem("admin_email");
    setUserEmail(null);
    router.push("/admin/login");
  };

  if (loading) {
    return (
      <div className="fixed inset-0 flex flex-col items-center justify-center bg-slate-950 z-[99999]">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600 flex items-center justify-center mb-6 shadow-xl shadow-indigo-900/50">
          <span className="text-white font-black text-sm">XMU</span>
        </div>
        <svg
          className="animate-spin h-6 w-6 text-indigo-400 mb-3"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        <span className="text-slate-400 text-xs font-medium tracking-widest uppercase">
          Verifying session…
        </span>
      </div>
    );
  }

  if (isLoginPage) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900 to-indigo-950 p-4 z-[9999]">
        {children}
      </div>
    );
  }

  return (
    <div className="fixed inset-0 flex flex-row bg-[#0b1020] text-slate-100 z-[9999] overflow-hidden antialiased">
      {/* OVERLAY: Muncul saat sidebar mobile aktif */}
      {mobileSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-sm transition-opacity duration-200"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* ── SIDEBAR RESPONSIVE ── */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-50 flex flex-col justify-between w-64 flex-shrink-0 bg-[#0f172a] border-r border-white/5 overflow-hidden transition-transform duration-300 ease-in-out ${
          mobileSidebarOpen
            ? "translate-x-0"
            : "-translate-x-full md:translate-x-0"
        }`}
      >
        <div className="relative">
          <div className="absolute inset-x-0 top-0 h-32 pointer-events-none bg-gradient-to-b from-indigo-500/10 to-transparent" />

          {/* Logo Section */}
          <div className="relative flex items-center justify-between px-5 py-5 border-b border-white/5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-900/60">
                <span className="text-white font-black text-xs">XMU</span>
              </div>
              <div>
                <p className="text-white font-bold text-sm leading-tight">
                  XMUM CMS
                </p>
                <p className="text-indigo-400 text-[10px] font-semibold uppercase tracking-widest">
                  Admin Portal
                </p>
              </div>
            </div>
            {/* Tombol Close Sidebar (Hanya muncul di HP) */}
            <button
              className="md:hidden text-slate-400 hover:text-white p-1"
              onClick={() => setMobileSidebarOpen(false)}
            >
              <IconClose />
            </button>
          </div>

          {/* Navigasi */}
          <nav className="relative px-3 pt-4 space-y-1">
            <NavItem
              href="/admin"
              label="Dashboard"
              icon={<IconDashboard />}
              active={pathname === "/admin"}
            />
            <NavItem
              href="/admin/knowledge"
              label="Knowledge Base"
              icon={<IconBook />}
              active={pathname.startsWith("/admin/knowledge")}
            />
            <NavItem
              href="/admin/logs"
              label="Conversation Logs"
              icon={<IconChat />}
              active={pathname.startsWith("/admin/logs")}
            />
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

        {/* User / Sign Out Area */}
        <div className="px-3 py-4 border-t border-white/5 bg-slate-900/40">
          <div className="flex items-center gap-3 px-3 py-2 mb-3">
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center font-bold text-xs text-white shrink-0">
              {userEmail ? userEmail.substring(0, 2).toUpperCase() : "AD"}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-white text-xs font-semibold truncate leading-tight">
                {userEmail}
              </p>
              <p className="text-slate-500 text-[10px] font-medium uppercase">
                Administrator
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-red-600/10 hover:bg-red-600 text-red-400 hover:text-white text-xs font-semibold rounded-xl transition-all border border-red-600/20"
          >
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── AREA KONTEN UTAMA ── */}
      <main className="flex-1 flex flex-col w-full">
        {/* Top Header */}
        <header className="h-14 bg-slate-900/80 border-b border-white/5 flex items-center justify-between px-4 sm:px-6 shrink-0 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            {/* Burger Button (Hanya muncul di HP) */}
            <button
              className="md:hidden text-slate-300 hover:text-white p-1.5 rounded-lg bg-white/5"
              onClick={() => setMobileSidebarOpen(true)}
            >
              <IconMenu />
            </button>
            <h1 className="text-slate-200 font-bold text-sm sm:text-base tracking-tight">
              {getPageTitle(pathname)}
            </h1>
          </div>

          <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 sm:px-3 sm:py-1.5 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-emerald-400 text-[10px] sm:text-[11px] font-semibold tracking-wide uppercase whitespace-nowrap">
              Real Data
            </span>
          </div>
        </header>

        {/* Scrollable Container - Tambahkan padding di sini */}
        <div className="flex-1 overflow-auto p-4 sm:p-6 lg:p-8 focus:outline-none">
          {children}
        </div>
      </main>
    </div>
  );
}
