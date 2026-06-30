"use client";

import React, { useEffect, useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import {
  getSuggestions,
  updateSuggestionStatus,
  Suggestion,
} from "@/services/suggestionService";

type FilterStatus = "all" | "pending" | "approved" | "rejected";

const STATUS_BADGE: Record<string, string> = {
  pending: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  approved: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  rejected: "bg-rose-500/15 text-rose-300 border-rose-500/30",
};

export default function SuggestionsPage() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [filter, setFilter] = useState<FilterStatus>("pending");
  const [loading, setLoading] = useState(true);
  const [actioningId, setActioningId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ msg: string; type: "ok" | "err" } | null>(null);
  const [adminEmail, setAdminEmail] = useState("");

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setAdminEmail(data?.session?.user?.email ?? "admin");
    });
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getSuggestions(
        filter === "all" ? undefined : filter
      );
      setSuggestions(data);
    } catch {
      showToast("Failed to load suggestions.", "err");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [filter]);

  const showToast = (msg: string, type: "ok" | "err") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAction = async (id: string, action: "approved" | "rejected") => {
    setActioningId(id);
    try {
      await updateSuggestionStatus(id, action, adminEmail);
      showToast(
        action === "approved" ? "Suggestion approved." : "Suggestion rejected.",
        "ok"
      );
      setSuggestions((prev) =>
        filter === "all"
          ? prev.map((s) =>
              s.id === id ? { ...s, status: action, reviewed_by: adminEmail } : s
            )
          : prev.filter((s) => s.id !== id)
      );
    } catch {
      showToast("Action failed. Please try again.", "err");
    } finally {
      setActioningId(null);
    }
  };

  return (
    <div className="w-full h-full p-8 lg:p-12">
      <div className="mx-auto max-w-5xl space-y-10">
        {/* Header */}
        <div className="space-y-1">
          <h2 className="text-3xl font-bold text-white">Suggested Questions</h2>
          <p className="text-slate-400">
            Review questions submitted by users. Approve to add to the knowledge
            base, or reject if irrelevant.
          </p>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 flex-wrap">
          {(["pending", "all", "approved", "rejected"] as FilterStatus[]).map(
            (s) => (
              <button
                key={s}
                id={`filter-tab-${s}`}
                onClick={() => setFilter(s)}
                className={`px-5 py-2 rounded-full text-sm font-semibold border transition-all ${
                  filter === s
                    ? "bg-indigo-600 border-indigo-500 text-white"
                    : "bg-slate-900/40 border-white/10 text-slate-400 hover:text-white hover:border-white/20"
                }`}
              >
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            )
          )}
        </div>

        {/* Table */}
        {loading ? (
          <p className="text-slate-500 text-sm">Loading...</p>
        ) : suggestions.length === 0 ? (
          <div className="rounded-2xl border border-white/5 bg-slate-900/30 p-16 text-center">
            <p className="text-slate-500 text-sm">No {filter} suggestions found.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {suggestions.map((s) => (
              <div
                key={s.id}
                className="rounded-2xl border border-white/5 bg-slate-900/40 p-6 space-y-4"
              >
                {/* Question */}
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="space-y-1 flex-1 min-w-0">
                    <p className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
                      Suggested Question
                    </p>
                    <p className="text-white font-semibold text-base leading-snug">
                      {s.question}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold border uppercase tracking-wide flex-shrink-0 ${STATUS_BADGE[s.status]}`}
                  >
                    {s.status}
                  </span>
                </div>

                {/* User's suggested answer (highlighted) */}
                {s.suggested_answer && (
                  <div className="rounded-xl bg-indigo-500/10 border border-indigo-500/20 px-4 py-3">
                    <p className="text-[11px] font-bold uppercase tracking-widest text-indigo-400 mb-1">
                      User&apos;s Suggested Answer
                    </p>
                    <p className="text-slate-200 text-sm leading-relaxed">
                      {s.suggested_answer}
                    </p>
                  </div>
                )}

                {/* Original context */}
                {s.user_message && (
                  <div className="rounded-xl bg-slate-800/50 border border-white/5 px-4 py-3">
                    <p className="text-[11px] font-bold uppercase tracking-widest text-slate-500 mb-1">
                      Original Chat Message
                    </p>
                    <p className="text-slate-400 text-sm italic">
                      &ldquo;{s.user_message}&rdquo;
                    </p>
                  </div>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between flex-wrap gap-3 pt-1">
                  <p className="text-xs text-slate-500">
                    {new Date(s.created_at).toLocaleString()}
                    {s.reviewed_by && ` · Reviewed by ${s.reviewed_by}`}
                  </p>

                  {s.status === "pending" && (
                    <div className="flex gap-3">
                      <button
                        id={`reject-btn-${s.id}`}
                        disabled={actioningId === s.id}
                        onClick={() => handleAction(s.id, "rejected")}
                        className="px-4 py-2 rounded-lg text-sm font-semibold border border-rose-500/30 text-rose-400 hover:bg-rose-500/10 transition-all disabled:opacity-40"
                      >
                        Reject
                      </button>
                      <button
                        id={`approve-btn-${s.id}`}
                        disabled={actioningId === s.id}
                        onClick={() => handleAction(s.id, "approved")}
                        className="px-4 py-2 rounded-lg text-sm font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all disabled:opacity-40"
                      >
                        {actioningId === s.id ? "Processing..." : "Approve"}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Toast */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 px-5 py-3 rounded-xl text-sm font-semibold shadow-xl z-50 ${
            toast.type === "ok"
              ? "bg-emerald-600 text-white"
              : "bg-rose-600 text-white"
          }`}
        >
          {toast.msg}
        </div>
      )}
    </div>
  );
}
