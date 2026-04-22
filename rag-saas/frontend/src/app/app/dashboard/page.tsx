"use client";

import { CheckCircle, MessageSquare, Upload, Key, AlertCircle, ChevronRight, TrendingUp, BarChart3 } from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Btn, ProgBar } from "@/components/ui/shared";
import { USAGE } from "@/lib/mock-data";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();

  const stats = [
    { label: "Queries Today", value: "8,142", change: "+12%", up: true, color: "var(--cy)" },
    { label: "Documents", value: "24", change: "+3 this week", up: true, color: "var(--vi)" },
    { label: "Storage Used", value: "6.2 GB", change: "of 50 GB", up: null, color: "var(--ok)" },
    { label: "Avg. Response", value: "94 ms", change: "-8% faster", up: true, color: "var(--warn)" },
  ];

  const activity = [
    { act: "Document indexed", detail: "Q3_Financial_Report.pdf — 847 chunks", time: "2 min ago", icon: <CheckCircle size={13} />, c: "var(--ok)" },
    { act: "API query", detail: "What are the main KPIs from Q3?", time: "5 min ago", icon: <MessageSquare size={13} />, c: "var(--cy)" },
    { act: "Document uploaded", detail: "Customer_Database.csv (12.8 MB)", time: "12 min ago", icon: <Upload size={13} />, c: "var(--vi)" },
    { act: "API key created", detail: "Production API key generated", time: "1 hour ago", icon: <Key size={13} />, c: "var(--warn)" },
    { act: "Usage alert", detail: "80% of monthly query quota reached", time: "3 hours ago", icon: <AlertCircle size={13} />, c: "var(--err)" },
  ];

  const quick = [
    { label: "Upload Document", icon: <Upload size={15} />, c: "var(--cy)", page: "/app/knowledge" },
    { label: "New Chat Session", icon: <MessageSquare size={15} />, c: "var(--vi)", page: "/app/chat" },
    { label: "View API Keys", icon: <Key size={15} />, c: "var(--ok)", page: "/app/api-keys" },
    { label: "Usage & Billing", icon: <BarChart3 size={15} />, c: "var(--warn)", page: "/app/settings" },
  ];

  return (
    <div>
      <div className="pghdr">
        <h1 className="pgtit">Dashboard</h1>
        <p className="pgsub">Welcome back, Alex. Here's what's happening with your knowledge base.</p>
      </div>

      <div className="sgrid">
        {stats.map((s, i) => (
          <div key={i} className="sc">
            <div style={{ position: "absolute", top: -20, right: -20, width: 80, height: 80, borderRadius: "50%", background: s.color, filter: "blur(26px)", opacity: .13 }} />
            <div className="sl">{s.label}</div>
            <div className="sv">{s.value}</div>
            <div className="scd" style={{ color: s.up === null ? "var(--tm)" : s.up ? "var(--ok)" : "var(--err)" }}>
              {s.up === true && <TrendingUp size={11} />}
              {s.up === false && <TrendingUp size={11} style={{ transform: "scaleY(-1)" }} />}
              {s.change}
            </div>
          </div>
        ))}
      </div>

      <div className="sec">
        <div className="g2" style={{ alignItems: "start" }}>
          <div>
            <div className="sechdr">
              <span className="sectit">Query Volume — 7 days</span>
              <span className="bdg bcy"><span className="livdot" />Live</span>
            </div>
            <div className="card" style={{ padding: "20px 14px 12px" }}>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={USAGE} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="cg" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--cy)" stopOpacity={0.18} />
                      <stop offset="95%" stopColor="var(--cy)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--tm)" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "var(--tm)" }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={{ background: "var(--s2)", border: "1px solid var(--b)", borderRadius: 8, fontSize: 12, color: "var(--tx)" }} itemStyle={{ color: "var(--cy)" }} cursor={{ stroke: "var(--b)" }} />
                  <Area type="monotone" dataKey="queries" stroke="var(--cy)" strokeWidth={2} fill="url(#cg)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div>
            <div className="sechdr"><span className="sectit">Recent Activity</span><Btn v="g" sm>View all</Btn></div>
            <div className="card">
              {activity.map((a, i) => (
                <div key={i} className="fx is gap10" style={{ padding: "13px 16px", borderBottom: i < activity.length - 1 ? "1px solid var(--b)" : "none" }}>
                  <div style={{ width: 28, height: 28, borderRadius: 7, background: a.c, display: "flex", alignItems: "center", justifyContent: "center", color: "#000", flexShrink: 0, marginTop: 1, opacity: .85 }}>{a.icon}</div>
                  <div className="f1" style={{ minWidth: 0 }}>
                    <div className="xs w6 mb4">{a.act}</div>
                    <div className="xs tm trunc">{a.detail}</div>
                  </div>
                  <span className="xs" style={{ color: "var(--ts)", flexShrink: 0 }}>{a.time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="sec">
        <div className="sechdr"><span className="sectit">Quick Actions</span></div>
        <div className="g2">
          {quick.map((q, i) => (
            <div key={i} className="card ptr fx ic gap12 p16" onClick={() => router.push(q.page)}>
              <div style={{ width: 36, height: 36, borderRadius: 9, background: q.c, display: "flex", alignItems: "center", justifyContent: "center", color: "#000", opacity: .85 }}>{q.icon}</div>
              <span className="base w5">{q.label}</span>
              <ChevronRight size={14} color="var(--tm)" style={{ marginLeft: "auto" }} />
            </div>
          ))}
        </div>
      </div>

      <div className="sec">
        <div className="sechdr"><span className="sectit">Monthly Usage</span><Btn v="p" sm onClick={() => router.push("/app/settings")}>Upgrade plan</Btn></div>
        <div className="card p24">
          <div className="g2">
            {[
              { label: "Queries", used: 8142, total: 10000, color: "var(--cy)" },
              { label: "Storage", used: 6.2, total: 50, unit: "GB", color: "var(--vi)" },
              { label: "Documents", used: 24, total: 500, color: "var(--ok)" },
              { label: "API Keys", used: 2, total: 10, color: "var(--warn)" },
            ].map((u, i) => {
              const pct = Math.round((u.used / u.total) * 100);
              return (
                <div key={i}>
                  <div className="fx jb ic mb6 xs"><span className="tm">{u.label}</span><span className="w5">{u.used.toLocaleString()}{u.unit ? " " + u.unit : ""} <span className="tm">/ {u.total}{u.unit ? " " + u.unit : ""}</span></span></div>
                  <ProgBar value={u.used} max={u.total} color={u.color} />
                  <div className="xs tm mt4">{pct}% used</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
