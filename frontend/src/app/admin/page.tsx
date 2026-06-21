"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabaseClient";

type BackendStatus = "checking" | "online" | "offline";

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    knowledgeCount: 0,
    academicCount: 0,
    campusLifeCount: 0,
    conversationCount: 0,
  });

  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/health`);
        setBackendStatus(response.ok ? "online" : "offline");
      } catch {
        setBackendStatus("offline");
      }
    };

    const fetchStats = async () => {
      try {
        const { data: knowledgeItems, error: knowledgeError } = await supabase
          .from("knowledge_items")
          .select("module");

        if (knowledgeError) {
          console.error("Error fetching knowledge items:", knowledgeError);
        }

        const total = knowledgeItems ? knowledgeItems.length : 0;
        const academic = knowledgeItems
          ? knowledgeItems.filter(
              (item) => item.module === "academic_navigation",
            ).length
          : 0;
        const campusLife = knowledgeItems
          ? knowledgeItems.filter((item) => item.module === "campus_life")
              .length
          : 0;

        let conversationCount = 0;
        try {
          const { count, error: logsError } = await supabase
            .from("conversation_logs")
            .select("*", { count: "exact", head: true });
          if (!logsError && count !== null) {
            conversationCount = count;
          }
        } catch (err) {
          console.error("Error querying conversation_logs count:", err);
        }

        setStats({
          knowledgeCount: total,
          academicCount: academic,
          campusLifeCount: campusLife,
          conversationCount: conversationCount,
        });
      } catch (err) {
        console.error("Error fetching stats:", err);
      } finally {
        setLoading(false);
      }
    };

    checkBackend();
    fetchStats();
  }, [backendUrl]);

  const statusConfig = {
    checking: {
      label: "Checking system...",
      dot: "bg-amber-400 animate-pulse",
      text: "text-amber-400",
      softBg: "bg-amber-500/10",
      border: "border-amber-500/20",
    },
    online: {
      label: "System Online",
      dot: "bg-emerald-400",
      text: "text-emerald-400",
      softBg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
    },
    offline: {
      label: "System Offline",
      dot: "bg-rose-400 animate-bounce",
      text: "text-rose-400",
      softBg: "bg-rose-500/10",
      border: "border-rose-500/20",
    },
  }[backendStatus];

  if (loading) {
    return (
      <div className="flex h-[60vh] w-full items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <svg
            className="animate-spin h-8 w-8 text-indigo-500"
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
          <span className="text-slate-400 text-sm font-medium tracking-wide">
            Loading dashboard data...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full text-slate-100 overflow-auto">
      <div className="mx-auto max-w-7xl space-y-8 lg:space-y-12">
        {/* BARIS 1: HERO / WELCOME & STATUS */}
        <section className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-indigo-900/20 to-slate-900/40 border border-white/5 p-6 rounded-2xl">
          <div>
            <h2 className="text-xl lg:text-2xl font-bold text-white">
              Welcome back, Admin!
            </h2>
            <p className="text-sm text-slate-400 mt-1">
              Here is what's happening with your system today.
            </p>
          </div>

          {/* Live API Health Status Badge */}
          <div
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${statusConfig.border} ${statusConfig.softBg}`}
          >
            <span className={`w-2 h-2 rounded-full ${statusConfig.dot}`} />
            <span
              className={`text-[11px] font-bold tracking-wide uppercase whitespace-nowrap ${statusConfig.text}`}
            >
              {statusConfig.label}
            </span>
          </div>
        </section>

        {/* BARIS 2: REAL STATS CARD (Using your custom StatCard component) */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <StatCard
            label="Total Knowledge Base"
            value={stats.knowledgeCount}
            helper="Aggregated markdown entries"
            accent="text-indigo-400"
          />
          <StatCard
            label="Academic Navigation"
            value={stats.academicCount}
            helper="Curriculum & maps data items"
          />
          <StatCard
            label="Campus Life"
            value={stats.campusLifeCount}
            helper="Events, housing & facility items"
          />
          <StatCard
            label="Conversation Logs"
            value={stats.conversationCount}
            helper="Total user interactions captured"
            accent="text-emerald-400"
          />
        </section>

        {/* BARIS 3: QUICK ACTIONS (Using your custom ActionCard component) */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ActionCard
            href="/admin/knowledge"
            eyebrow="CMS Management"
            title="Manage Knowledge Base"
            description="Add, edit, or remove context items feeding your LLM backend. Organize content into Academic or Campus Life categories."
            cta="Go to Knowledge Base"
          />
          <ActionCard
            href="/admin/logs"
            eyebrow="Analytics & Audits"
            title="Review Chat History"
            description="Inspect real-time conversation logs to pinpoint hallucination issues, user frustration trends, or unhandled inquiries."
            cta="Open Logs Viewer"
          />
        </section>

        {/* BARIS 4: VISUALIZATION PLACEHOLDER */}
        <section className="bg-slate-900/30 border border-white/5 rounded-2xl h-64 flex items-center justify-center p-6">
          <span className="text-sm text-slate-500 italic">
            System Charts & Analytics Visualization Container
          </span>
        </section>
      </div>
    </div>
  );
}

/* ──────────────────────────────────────────
   Your Reusable Component Deliverables
────────────────────────────────────────── */
function StatCard({
  label,
  value,
  helper,
  accent = "text-slate-100",
}: {
  label: string;
  value: number;
  helper: string;
  accent?: string;
}) {
  return (
    <div className="rounded-2xl border border-white/5 bg-slate-900/50 p-5">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        {label}
      </p>
      <div className="mt-4">
        <span className={`text-3xl font-bold tracking-tight ${accent}`}>
          {value.toLocaleString()}
        </span>
      </div>
      <p className="mt-3 text-xs text-slate-500">{helper}</p>
    </div>
  );
}

function ActionCard({
  href,
  eyebrow,
  title,
  description,
  cta,
}: {
  href: string;
  eyebrow: string;
  title: string;
  description: string;
  cta: string;
}) {
  return (
    <Link
      href={href}
      className="group rounded-2xl border border-white/5 bg-slate-900/20 p-6 transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-900/50 hover:border-white/10"
    >
      <div className="flex h-full flex-col justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-indigo-400">
            {eyebrow}
          </p>
          <h3 className="mt-2 text-lg font-bold tracking-tight text-white transition group-hover:text-indigo-300">
            {title}
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-slate-400">
            {description}
          </p>
        </div>
        <div className="mt-6 inline-flex items-center gap-2 text-xs font-semibold text-slate-200">
          {cta}
          <span className="transition-transform group-hover:translate-x-1">
            →
          </span>
        </div>
      </div>
    </Link>
  );
}
