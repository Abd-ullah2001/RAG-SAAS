"use client";

import React, { useState } from "react";
import { CheckCircle, XCircle, Clock, Copy, Check } from "lucide-react";

export function Badge({ t = "gray", children }: { t?: string, children: React.ReactNode }) {
  const m: Record<string, string> = { ok: "bdg bok", warn: "bdg bwarn", err: "bdg berr", cy: "bdg bcy", vi: "bdg bvi", gray: "bdg bgray" };
  const ic: Record<string, React.ReactNode> = { ok: <CheckCircle size={10} />, err: <XCircle size={10} />, warn: <Clock size={10} /> };
  return <span className={m[t] || "bdg bgray"}>{ic[t]}{children}</span>;
}

export function Btn({ v = "s", sm, lg, children, onClick, cls = "", style, disabled }: any) {
  const m: Record<string, string> = { p: "btn bp", s: "btn bs", g: "btn bg", d: "btn bd_" };
  return (
    <button
      className={`${m[v] || "btn bs"}${sm ? " sm" : ""}${lg ? " lg" : ""} ${cls}`}
      style={style}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

export function Inp({ placeholder, value, onChange, type = "text", cls = "", style, disabled, ...r }: any) {
  return (
    <input
      className={`inp ${cls}`}
      style={style}
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      disabled={disabled}
      {...r}
    />
  );
}

export function Toggle({ on, onToggle }: { on: boolean; onToggle: () => void }) {
  return (
    <div className={`tog${on ? " on" : ""}`} onClick={onToggle}>
      <div className="tth" />
    </div>
  );
}

export function ProgBar({ value, max = 100, color = "var(--cy)" }: { value: number; max?: number; color?: string }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className="pt">
      <div className="pf" style={{ width: `${pct}%`, background: pct > 80 ? "var(--err)" : color }} />
    </div>
  );
}

export function CodeBlk({ lang = "bash", code }: { lang?: string; code: string }) {
  const [cp, setCp] = useState(false);
  return (
    <div className="cblk">
      <div className="chdr">
        <span>{lang}</span>
        <button
          className="btn bg sm"
          style={{ padding: "3px 8px" }}
          onClick={() => {
            navigator.clipboard?.writeText(code);
            setCp(true);
            setTimeout(() => setCp(false), 2000);
          }}
        >
          {cp ? <><Check size={10} /> Copied</> : <><Copy size={10} /> Copy</>}
        </button>
      </div>
      <div className="cbdy">{code}</div>
    </div>
  );
}
