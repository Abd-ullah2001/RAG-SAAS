"use client";

import { Zap, Search, Activity, FileText, Layers, Shield, ArrowRight, Eye, CheckCircle, Sparkles } from "lucide-react";
import { Btn } from "@/components/ui/shared";
import { useRouter } from "next/navigation";

export default function Landing() {
  const router = useRouter();

  const feats = [
    { icon: <Zap size={20} />, bg: "var(--cy-d)", ic: "var(--cy)", title: "Blazing Fast Retrieval", desc: "Sub-100ms semantic search across millions of documents using vector embeddings and ANN indexing." },
    { icon: <Search size={20} />, bg: "var(--vi-d)", ic: "var(--vi)", title: "Semantic Understanding", desc: "Go beyond keywords. Our models understand context, intent, and nuance in natural language queries." },
    { icon: <Activity size={20} />, bg: "rgba(52,211,153,.1)", ic: "var(--ok)", title: "Real-time Streaming", desc: "Stream AI responses token-by-token via SSE for an instant, ChatGPT-like experience in your app." },
    { icon: <FileText size={20} />, bg: "rgba(251,191,36,.1)", ic: "var(--warn)", title: "Source Citations", desc: "Every answer links back to the exact document chunk used as evidence. Full transparency, always." },
    { icon: <Layers size={20} />, bg: "rgba(244,114,182,.1)", ic: "#f472b6", title: "Multi-format Support", desc: "PDF, DOCX, CSV, TXT, Markdown — upload anything. We handle chunking, cleaning, and embedding." },
    { icon: <Shield size={20} />, bg: "rgba(96,165,250,.1)", ic: "#60a5fa", title: "Enterprise Security", desc: "SOC 2 Type II compliant. Data encrypted at rest and in transit. Per-tenant isolation built in." },
  ];
  const plans = [
    { name: "Starter", price: "$0", per: "/month", desc: "For developers exploring RAG", feats: ["100 queries / month", "5 documents (50 MB)", "1 API key", "Community support"], cta: "Start free", v: "s", feat: false },
    { name: "Pro", price: "$49", per: "/month", desc: "For production apps and growing teams", feats: ["10,000 queries / month", "500 documents (5 GB)", "10 API keys", "Streaming responses", "Source citations", "Priority support"], cta: "Start free trial", v: "p", feat: true },
    { name: "Enterprise", price: "Custom", per: "", desc: "For mission-critical deployments", feats: ["Unlimited queries", "Unlimited storage", "Custom embedding models", "SSO & SAML", "SLA guarantees", "Dedicated support"], cta: "Contact sales", v: "s", feat: false },
  ];

  return (
    <div className="land">
      <nav className="lnav">
        <div className="fx ic gap10" style={{ fontFamily: "var(--fd)", fontSize: 17, fontWeight: 700, color: "var(--cy)" }}>
          <div className="lmark">R</div>RAG<span className="cy">saas</span>
        </div>
        <div className="fx ic gap16">
          {["Docs", "Pricing", "Blog"].map(l => <span key={l} style={{ fontSize: 13, color: "var(--tm)", cursor: "pointer" }}>{l}</span>)}
          <Btn v="g" sm onClick={() => router.push("/auth")}>Sign in</Btn>
          <Btn v="p" sm onClick={() => router.push("/auth")}>Get started</Btn>
        </div>
      </nav>

      {/* Hero */}
      <div className="hero">
        <div className="hgrid" /><div className="hglow" />
        <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <div className="hbadge"><Sparkles size={12} /> RAG-powered Knowledge Engine</div>
          <h1 className="htit">Build AI apps that<br /><span className="cy">actually know</span> your data</h1>
          <p className="hsub">Drop in your documents. Get a blazing-fast semantic search API, streaming chat, and source citations — in minutes.</p>
          <div className="fx ic gap12">
            <Btn v="p" lg onClick={() => router.push("/auth")}><ArrowRight size={14} />Start for free</Btn>
            <Btn v="s" lg onClick={() => router.push("/app/dashboard")}><Eye size={14} />Live demo</Btn>
          </div>
          <div className="fx ic gap16" style={{ marginTop: 40, color: "var(--tm)", fontSize: 13 }}>
            {[["4,000+", "developers"], ["12M+", "queries / month"], ["99.9%", "uptime SLA"]].map(([val, lbl]) => (
              <div key={lbl} style={{ textAlign: "center" }}>
                <div style={{ fontFamily: "var(--fd)", fontSize: 22, fontWeight: 700, color: "var(--tx)", letterSpacing: "-1px" }}>{val}</div>
                <div>{lbl}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <div style={{ padding: "20px 60px 16px", textAlign: "center", marginBottom: 32 }}>
        <h2 style={{ fontFamily: "var(--fd)", fontSize: 32, fontWeight: 800, letterSpacing: "-1px", marginBottom: 10 }}>Everything you need</h2>
        <p style={{ color: "var(--tm)", fontSize: 15 }}>A complete RAG platform, not just an API</p>
      </div>
      <div className="fgrid">
        {feats.map((f, i) => (
          <div key={i} className="fcard">
            <div className="fico" style={{ background: f.bg }}><span style={{ color: f.ic }}>{f.icon}</span></div>
            <div className="ftit">{f.title}</div>
            <p className="fdesc">{f.desc}</p>
          </div>
        ))}
      </div>

      {/* Pricing */}
      <div style={{ padding: "0 60px 16px", textAlign: "center", marginBottom: 32 }}>
        <h2 style={{ fontFamily: "var(--fd)", fontSize: 32, fontWeight: 800, letterSpacing: "-1px", marginBottom: 10 }}>Simple pricing</h2>
        <p style={{ color: "var(--tm)", fontSize: 15 }}>Start free. Scale as you grow.</p>
      </div>
      <div className="pgrid">
        {plans.map((p, i) => (
          <div key={i} className={`pcard${p.feat ? " pfeat" : ""}`}>
            {p.feat && <div className="pbadge">MOST POPULAR</div>}
            <div className="pname">{p.name}</div>
            <div className="pval">{p.price}</div>
            <div className="pper">{p.per}&nbsp;{p.desc}</div>
            <div className="hr mb20" />
            <div className="mb24">{p.feats.map((f, j) => <div key={j} className="pfeat"><CheckCircle size={13} color="var(--ok)" />{f}</div>)}</div>
            <Btn v={p.v} cls="wf" style={{ justifyContent: "center" }} onClick={() => router.push("/auth")}>{p.cta}</Btn>
          </div>
        ))}
      </div>

      {/* CTA footer */}
      <div style={{ padding: "20px 60px 60px", textAlign: "center" }}>
        <div className="hl" style={{ maxWidth: 560, margin: "0 auto" }}>
          <h3 style={{ fontFamily: "var(--fd)", fontSize: 24, fontWeight: 800, letterSpacing: "-.5px", marginBottom: 8 }}>Ready to build?</h3>
          <p style={{ color: "var(--tm)", fontSize: 14, marginBottom: 20 }}>Join 4,000+ developers building smarter AI apps with RAGsaas.</p>
          <Btn v="p" lg onClick={() => router.push("/auth")}><ArrowRight size={14} />Get started free</Btn>
        </div>
      </div>
    </div>
  );
}
