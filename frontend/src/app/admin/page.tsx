"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabaseClient";

type BackendStatus = "checking" | "online" | "offline";

export default function MockAdminDashboard() {
  const [stats, setStats] = useState({
    knowledgeCount: 0,
    academicCount: 0,
    campusLifeCount: 0,
    conversationCount: 0,
  });

  const [backendUrl, setBackendUrl] = useState("");
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    setBackendUrl(url);

    const checkBackend = async () => {
      try {
        const response = await fetch(`${url}/api/health`);
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

        if (knowledgeItems) {
          const total = knowledgeItems.length;
          const academic = knowledgeItems.filter(
            (item) => item.module === "academic_navigation"
          ).length;
          const campusLife = knowledgeItems.filter(
            (item) => item.module === "campus_life"
          ).length;

          setStats({
            knowledgeCount: total,
            academicCount: academic,
            campusLifeCount: campusLife,
            conversationCount: conversationCount,
          });
        }
      } catch (err) {
        console.error("Error fetching stats:", err);
      } finally {
        setLoading(false);
      }
    };

    checkBackend();
    fetchStats();
  }, []);

  const statusConfig = {
    checking: {
      label: "Checking connection",
      dot: "bg-amber-400",
      text: "text-amber-300",
      softBg: "bg-amber-500/10",
      border: "border-amber-400/20",
    },
    online: {
      label: "System online",
      dot: "bg-emerald-400",
      text: "text-emerald-300",
      softBg: "bg-emerald-500/10",
      border: "border-emerald-400/20",
    },
    offline: {
      label: "System offline",
      dot: "bg-rose-400",
      text: "text-rose-300",
      softBg: "bg-rose-500/10",
      border: "border-rose-400/20",
    },
  }[backendStatus];

  return (
    <div className="min-h-screen bg-[#0b1020] text-slate-100 antialiased">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10">
        <div className="space-y-8 lg:space-y-10">
          {/* =========================================================
              1) HERO / DASHBOARD OVERVIEW
          ========================================================= */}
          <section className="overflow-hidden rounded-[32px] border border-white/10 bg-[#111827] shadow-[0_20px_80px_rgba(0,0,0,0.35)]">
            <div className="grid lg:grid-cols-[1.45fr_0.95fr]">
              <div className="p-7 sm:p-9 lg:p-12">
                <div className="inline-flex items-center rounded-full border border-blue-400/20 bg-blue-500/10 px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-blue-300">
                  XMUM Chatbot CMS
                </div>

                <div className="mt-6 max-w-2xl pa">
                  <h1 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                    Admin dashboard
                  </h1>
                  <p className="mt-4 max-w-xl text-sm leading-7 text-slate-400 sm:text-[15px]">
                    Manage chatbot knowledge, review conversation logs, and monitor
                    platform health from one workspace.
                  </p>
                </div>

                <div className="mt-10 flex flex-col gap-3 sm:flex-row">
                  <Link
                    href="/admin/knowledge"
                    className="inline-flex items-center justify-center rounded-2xl bg-blue-500 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-blue-400"
                  >
                    Open Knowledge Base
                  </Link>

                  <Link
                    href="/admin/logs"
                    className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] px-5 py-3.5 text-sm font-semibold text-slate-200 transition hover:bg-white/[0.06]"
                  >
                    View Conversation Logs
                  </Link>
                </div>
              </div>

              <div className="border-t border-white/10 bg-[#0f172a] p-7 sm:p-9 lg:border-l lg:border-t-0 lg:p-10">
                <div className="flex h-full flex-col justify-between gap-6">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                      System status
                    </p>

                    <div
                      className={`mt-4 inline-flex items-center gap-2 rounded-full border px-3.5 py-2 text-sm font-medium ${statusConfig.softBg} ${statusConfig.border} ${statusConfig.text}`}
                    >
                      <span
                        className={`h-2.5 w-2.5 rounded-full ${statusConfig.dot} ${
                          backendStatus === "checking" || backendStatus === "online"
                            ? "animate-pulse"
                            : ""
                        }`}
                      />
                      {statusConfig.label}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                      API endpoint
                    </p>
                    <div className="mt-3 rounded-xl bg-black/20 px-3 py-3 font-mono text-xs leading-6 text-slate-300 break-all">
                      {backendUrl || "http://localhost:8000"}
                    </div>
                  </div>

                  <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-5">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">
                      Environment note
                    </p>
                    <p className="mt-3 text-sm leading-7 text-slate-400">
                      If the dashboard cannot reach the backend, verify the API
                      base URL and environment variables before checking client-side errors.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* =========================================================
              2) KPI / STATS ROW WITH SECTION PADDING
          ========================================================= */}
          <section className="rounded-[32px] border border-white/10 bg-[#111827] px-6 py-7 shadow-sm sm:px-7 sm:py-8 lg:px-8 lg:py-9">
            <div>
              <h2 className="text-sm font-semibold text-slate-100">Overview</h2>
              <p className="mt-1.5 text-sm text-slate-400">
                Quick snapshot of chatbot content and activity.
              </p>
            </div>

            <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatCard
                label="Total Q&A Items"
                value={stats.knowledgeCount}
                helper="Knowledge entries"
                accent="text-blue-400"
              />
              <StatCard
                label="Academic Topics"
                value={stats.academicCount}
                helper="Academic category items"
              />
              <StatCard
                label="Campus Life Topics"
                value={stats.campusLifeCount}
                helper="Campus support content"
              />
              <StatCard
                label="Conversation Logs"
                value={stats.conversationCount}
                helper="Tracked interactions"
                accent="text-emerald-400"
              />
            </div>
          </section>

          {/* =========================================================
              3) WORKSPACE ROW WITH SECTION PADDING
          ========================================================= */}
          {/* <section className="rounded-[32px] border border-white/10 bg-[#111827] px-6 py-7 shadow-sm sm:px-7 sm:py-8 lg:px-8 lg:py-9">
            <div>
              <h2 className="text-sm font-semibold text-slate-100">Workspace</h2>
              <p className="mt-1.5 text-sm text-slate-400">
                Go directly to the areas you manage most often.
              </p>
            </div>

            <div className="mt-6 grid gap-5 lg:grid-cols-2">
              <ActionCard
                href="/admin/knowledge"
                eyebrow="Content management"
                title="Knowledge Base"
                description="Create, edit, and organize chatbot answers, academic content, and campus information."
                cta="Open knowledge workspace"
              />

              <ActionCard
                href="/admin/logs"
                eyebrow="Monitoring"
                title="Conversation Logs"
                description="Review user conversations, inspect fallback cases, and trace issues in chatbot responses."
                cta="Open logs"
              />
            </div>
          </section> */}

          {/* =========================================================
              4) SYSTEM OVERVIEW
          ========================================================= */}
          <section className="rounded-[32px] border border-white/10 bg-[#111827] px-6 py-7 shadow-[0_20px_80px_rgba(0,0,0,0.25)] sm:px-7 sm:py-8 lg:px-8 lg:py-10">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-2xl">
                <h2 className="text-sm font-semibold text-slate-100">
                  System overview
                </h2>
                <p className="mt-3 text-sm leading-7 text-slate-400">
                  Operational details for the current admin environment. This area
                  is meant for infrastructure visibility rather than primary navigation.
                </p>
              </div>

              <div
                className={`inline-flex w-fit items-center gap-2 rounded-full border px-3.5 py-2 text-sm font-medium ${statusConfig.softBg} ${statusConfig.border} ${statusConfig.text}`}
              >
                <span
                  className={`h-2.5 w-2.5 rounded-full ${statusConfig.dot} ${
                    backendStatus === "checking" || backendStatus === "online"
                      ? "animate-pulse"
                      : ""
                  }`}
                />
                {statusConfig.label}
              </div>
            </div>

            <div className="mt-8 grid gap-5 lg:grid-cols-3">
              <InfoCard
                label="Backend"
                value={
                  backendStatus === "checking"
                    ? "Checking"
                    : backendStatus === "online"
                    ? "Online"
                    : "Offline"
                }
                description="Current API health check result."
              />

              <InfoCard
                label="API Base URL"
                value={backendUrl || "http://localhost:8000"}
                description="Environment target used by the dashboard."
                mono
              />

              <InfoCard
                label="Data Layer"
                value="Supabase (active)"
                description="Real-time data synchronization with Supabase."
              />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

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
    <div className="rounded-3xl border border-white/10 bg-[#0f172a] p-6">
      <p className="text-sm font-medium text-slate-400">{label}</p>
      <div className="mt-6">
        <span className={`text-4xl font-semibold tracking-tight ${accent}`}>
          {value}
        </span>
      </div>
      <p className="mt-5 text-sm text-slate-500">{helper}</p>
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
      className="group rounded-[28px] border border-white/10 bg-[#0f172a] p-7 transition hover:-translate-y-0.5 hover:bg-[#141d2f]"
    >
      <div className="flex h-full flex-col">
        <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">
          {eyebrow}
        </p>

        <h3 className="mt-4 text-2xl font-semibold tracking-tight text-white transition group-hover:text-blue-300">
          {title}
        </h3>

        <p className="mt-4 max-w-xl text-sm leading-7 text-slate-400">
          {description}
        </p>

        <div className="mt-10 inline-flex items-center gap-2 text-sm font-semibold text-slate-200">
          {cta}
          <span className="transition-transform group-hover:translate-x-1">→</span>
        </div>
      </div>
    </Link>
  );
}

function InfoCard({
  label,
  value,
  description,
  mono = false,
}: {
  label: string;
  value: string;
  description: string;
  mono?: boolean;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-[#0f172a] p-6">
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500">
        {label}
      </p>
      <div
        className={`mt-4 text-sm leading-7 text-slate-200 break-all ${
          mono ? "font-mono" : "font-medium"
        }`}
      >
        {value}
      </div>
      <p className="mt-4 text-sm leading-7 text-slate-400">{description}</p>
    </div>
  );
}