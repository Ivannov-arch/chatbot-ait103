"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Check if mock session exists
  useEffect(() => {
    const isLoggedIn = localStorage.getItem("admin_logged_in");
    if (isLoggedIn === "true") {
      router.push("/admin");
    }
  }, [router]);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    setSuccessMsg("");

    // Simulate network delay
    setTimeout(() => {
      // Mock login check (Accepts any email ending with admin, or admin@xmum.edu.my / admin)
      if (email === "admin@xmum.edu.my" && password === "admin123") {
        localStorage.setItem("admin_logged_in", "true");
        localStorage.setItem("admin_email", email);
        setSuccessMsg("Login successful! Redirecting...");
        setTimeout(() => {
          router.push("/admin");
        }, 800);
      } else {
        setErrorMsg("Invalid credentials. Try admin@xmum.edu.my and password admin123");
        setLoading(false);
      }
    }, 600);
  };

  return (
    <div className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden font-sans">
      {/* Header */}
      <div className="bg-[#1a3a5c] p-8 text-center text-white">
        <div className="w-16 h-16 bg-[#2e6da4] rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4 border-2 border-white/20">
          XMU
        </div>
        <h1 className="text-xl font-semibold tracking-tight">Admin Portal CMS</h1>
        <p className="text-sm text-slate-300 mt-1">Sign in to manage chatbot knowledge base (Mock Mode)</p>
      </div>

      {/* Form */}
      <form onSubmit={handleLogin} className="p-8 space-y-6">
        <div className="p-3 bg-blue-50 border border-blue-200 text-blue-800 text-[11px] rounded-lg">
          💡 <b>Mock Credentials:</b><br />
          Email: <code className="font-mono">admin@xmum.edu.my</code><br />
          Password: <code className="font-mono">admin123</code>
        </div>

        {errorMsg && (
          <div className="p-3.5 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-2">
            <span>⚠️</span>
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="p-3.5 bg-green-50 border border-green-200 text-green-700 text-xs rounded-lg flex items-center gap-2">
            <span>✅</span>
            <span>{successMsg}</span>
          </div>
        )}

        <div className="space-y-1.5">
          <label htmlFor="email" className="block text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Email Address
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={loading}
            placeholder="admin@xmum.edu.my"
            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#2e6da4] focus:border-transparent text-sm text-slate-800 transition-all placeholder:text-slate-400"
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="password" className="block text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            placeholder="••••••••"
            className="w-full px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-[#2e6da4] focus:border-transparent text-sm text-slate-800 transition-all placeholder:text-slate-400"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-4 bg-[#1a3a5c] hover:bg-[#2e6da4] text-white font-medium rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#2e6da4] disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 cursor-pointer shadow-md"
        >
          {loading ? "Signing in..." : "Sign In"}
        </button>

        <div className="pt-2 text-center">
          <a
            href="/"
            className="text-xs text-slate-500 hover:text-[#2e6da4] transition-all hover:underline"
          >
            ← Back to Campus Assistant Chatbot
          </a>
        </div>
      </form>
    </div>
  );
}
