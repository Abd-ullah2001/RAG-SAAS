"use client";

import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, Database, MessageSquare, Key, Settings, LogOut, User } from "lucide-react";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  const navs = [
    { icon: <LayoutDashboard size={15} />, label: "Dashboard", page: "/app/dashboard" },
    { icon: <Database size={15} />, label: "Knowledge Base", page: "/app/knowledge" },
    { icon: <MessageSquare size={15} />, label: "Chat Console", page: "/app/chat" },
    { icon: <Key size={15} />, label: "API Keys", page: "/app/api-keys" },
    { icon: <Settings size={15} />, label: "Settings", page: "/app/settings" },
  ];

  return (
    <div className="app">
      <div className="sidebar">
        <div className="logo" onClick={() => router.push("/")}>
          <div className="lmark">R</div>RAG<span className="cy">saas</span>
        </div>
        <div className="navs">
          {navs.map((n) => (
            <div
              key={n.page}
              className={`ni${pathname === n.page ? " on" : ""}`}
              onClick={() => router.push(n.page)}
            >
              {n.icon} {n.label}
            </div>
          ))}
        </div>
        <div className="nb">
          <div className="uinfo">
            <div className="av">A</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--tx)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>Alex Johnson</div>
              <div style={{ fontSize: 11, color: "var(--tm)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>Pro Plan</div>
            </div>
            <LogOut size={14} color="var(--tm)" style={{ cursor: "pointer" }} onClick={() => router.push("/")} />
          </div>
        </div>
      </div>
      <div className="main">
        {children}
      </div>
    </div>
  );
}
