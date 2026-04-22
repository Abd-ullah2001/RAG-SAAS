"use client";

import { useState } from "react";
import { Eye, EyeOff, Zap, Activity, FileText, Shield } from "lucide-react";
import { Btn, Inp } from "@/components/ui/shared";
import { useRouter } from "next/navigation";

export default function Auth() {
  const router = useRouter();
  const [tab, setTab] = useState("login");
  const [showPw, setShowPw] = useState(false);
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [name, setName] = useState("");

  return (
    <div className="auth">
      <div className="authl">
        <div style={{ position: "absolute", top: "-10%", left: "15%", width: 500, height: 500, background: "radial-gradient(ellipse, rgba(34,211,238,.05) 0%, transparent 65%)", pointerEvents: "none" }} />
        <div style={{ position: "relative", zIndex: 1 }}>
          <div className="fx ic gap10 mb24" style={{ fontFamily: "var(--fd)", fontSize: 18, fontWeight: 700, color: "var(--cy)", paddingBottom: 24, borderBottom: "1px solid var(--b)" }}>
            <div className="lmark">R</div>RAG<span className="cy">saas</span>
          </div>
          <h2 style={{ fontFamily: "var(--fd)", fontSize: 28, fontWeight: 700, letterSpacing: "-.7px", marginBottom: 12 }}>Your documents,<br />superpowered.</h2>
          <p style={{ color: "var(--tm)", fontSize: 14, lineHeight: 1.7, marginBottom: 36 }}>Upload files and start querying them with AI in under 5 minutes. No complex setup required.</p>
          <div className="fx fxc gap14">
            {[
              { icon: <Zap size={15} color="var(--cy)" />, text: "Semantic search across all your documents" },
              { icon: <Activity size={15} color="var(--ok)" />, text: "Real-time streaming responses" },
              { icon: <FileText size={15} color="var(--vi)" />, text: "Cited sources for every answer" },
              { icon: <Shield size={15} color="#60a5fa" />, text: "Enterprise-grade security" },
            ].map((item, i) => (
              <div key={i} className="fx ic gap10" style={{ fontSize: 13, color: "var(--tm)" }}>
                <div style={{ background: "var(--s2)", border: "1px solid var(--b)", borderRadius: 8, padding: 6, display: "flex" }}>{item.icon}</div>
                {item.text}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="authr">
        <div className="aform">
          <div style={{ textAlign: "center", marginBottom: 24 }}>
            <div className="lmark" style={{ margin: "0 auto 12px", width: 40, height: 40, fontSize: 16 }}>R</div>
            <h3 style={{ fontFamily: "var(--fd)", fontSize: 20, fontWeight: 700, marginBottom: 4 }}>
              {tab === "login" ? "Welcome back" : "Create your account"}
            </h3>
            <p style={{ color: "var(--tm)", fontSize: 13 }}>{tab === "login" ? "Sign in to your RAGsaas account" : "Start building — it's free"}</p>
          </div>

          <div className="atabs">
            <button className={`atab${tab === "login" ? " on" : ""}`} onClick={() => setTab("login")}>Sign in</button>
            <button className={`atab${tab === "signup" ? " on" : ""}`} onClick={() => setTab("signup")}>Sign up</button>
          </div>

          {/* OAuth */}
          <Btn v="s" cls="wf mb12" style={{ justifyContent: "center" }}>
            <svg width="15" height="15" viewBox="0 0 24 24"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" /><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" /><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" /><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" /></svg>
            Continue with Google
          </Btn>
          <div className="divl">or</div>

          {tab === "signup" && (
            <div className="fgrp">
              <label className="flabel">Full name</label>
              <Inp placeholder="Alex Johnson" value={name} onChange={(e: any) => setName(e.target.value)} />
            </div>
          )}
          <div className="fgrp">
            <label className="flabel">Email address</label>
            <Inp placeholder="you@company.com" type="email" value={email} onChange={(e: any) => setEmail(e.target.value)} />
          </div>
          <div className="fgrp">
            <label className="flabel">Password</label>
            <div className="rel">
              <Inp placeholder="••••••••••" type={showPw ? "text" : "password"} value={pw} onChange={(e: any) => setPw(e.target.value)} />
              <button style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--tm)" }} onClick={() => setShowPw(!showPw)}>
                {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
          </div>

          {tab === "login" && <div style={{ textAlign: "right", marginBottom: 14 }}><span style={{ fontSize: 12, color: "var(--cy)", cursor: "pointer" }}>Forgot password?</span></div>}

          <Btn v="p" cls="wf" style={{ justifyContent: "center", padding: 11 }} onClick={() => router.push("/app/dashboard")}>
            {tab === "login" ? "Sign in to dashboard" : "Create free account"}
          </Btn>

          {tab === "signup" && (
            <p style={{ fontSize: 11, color: "var(--tm)", textAlign: "center", marginTop: 12, lineHeight: 1.6 }}>
              By creating an account you agree to our <span style={{ color: "var(--cy)" }}>Terms of Service</span> and <span style={{ color: "var(--cy)" }}>Privacy Policy</span>.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
