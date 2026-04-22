"use client";

import { useState, useRef } from "react";
import { Upload, Search, Trash2, FileText, CheckCircle, XCircle, Clock } from "lucide-react";
import { Btn, Inp, Badge, Toggle } from "@/components/ui/shared";
import { DOCS } from "@/lib/mock-data";

export default function KnowledgeBase() {
  const [docs, setDocs] = useState(DOCS);
  const [q, setQ] = useState("");
  const [over, setOver] = useState(false);
  const ref = useRef<HTMLInputElement>(null);

  const typeC: Record<string, string> = { PDF: "var(--err)", CSV: "var(--ok)", DOCX: "var(--cy)" };
  const filtered = docs.filter(d => d.name.toLowerCase().includes(q.toLowerCase()));

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setOver(false);
    // In a real app, process e.dataTransfer.files here
    alert("File upload simulation started.");
  };

  const toggleDoc = (id: number) => {
    setDocs(docs.map(d => d.id === id ? { ...d, on: !d.on } : d));
  };

  return (
    <div>
      <div className="pghdr">
        <h1 className="pgtit">Knowledge Base</h1>
        <p className="pgsub">Upload documents, manage your vector indices, and configure context.</p>
      </div>

      <div className="sec">
        <div
          className={`dz mb24 ${over ? "over" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setOver(true); }}
          onDragLeave={() => setOver(false)}
          onDrop={handleDrop}
          onClick={() => ref.current?.click()}
        >
          <input type="file" ref={ref} style={{ display: "none" }} multiple />
          <Upload size={32} color="var(--cy)" style={{ margin: "0 auto 16px" }} />
          <div className="w6 base mb4">Click or drag files to upload</div>
          <div className="xs tm">Supports PDF, DOCX, CSV, TXT (Max 50MB)</div>
        </div>

        <div className="card">
          <div className="fx jb ic p16" style={{ borderBottom: "1px solid var(--b)" }}>
            <div className="w6">Your Documents</div>
            <div className="fx ic gap12">
              <div className="rel">
                <Search size={14} color="var(--tm)" className="abs" style={{ left: 12, top: "50%", transform: "translateY(-50%)" }} />
                <Inp placeholder="Search files..." value={q} onChange={(e: any) => setQ(e.target.value)} style={{ paddingLeft: 34, width: 220 }} />
              </div>
              <Btn v="g" sm><Trash2 size={13} /> Delete all</Btn>
            </div>
          </div>
          <table className="tbl">
            <thead>
              <tr>
                <th>Document</th>
                <th>Status</th>
                <th>Size</th>
                <th>Chunks</th>
                <th>Uploaded</th>
                <th style={{ textAlign: "right" }}>Active Context</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(d => (
                <tr key={d.id}>
                  <td>
                    <div className="fx ic gap10">
                      <div style={{ width: 28, height: 28, borderRadius: 6, background: "var(--s2)", border: "1px solid var(--b)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <FileText size={14} style={{ color: typeC[d.type] || "var(--tm)" }} />
                      </div>
                      <div className="f1 trunc" style={{ maxWidth: 200 }}>
                        <div className="w5 mb4 trunc">{d.name}</div>
                        <div className="xs tm">{d.type}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    {d.status === "indexed" && <Badge t="ok">Indexed</Badge>}
                    {d.status === "processing" && <Badge t="warn"><span className="livdot" style={{ background: "var(--warn)", width: 5, height: 5 }} />Processing</Badge>}
                    {d.status === "failed" && <Badge t="err">Failed</Badge>}
                  </td>
                  <td className="tm">{d.size}</td>
                  <td className="tm">{d.chunks}</td>
                  <td className="tm">{d.date}</td>
                  <td>
                    <div className="fx jb ic" style={{ justifyContent: "flex-end" }}>
                      <Toggle on={d.on} onToggle={() => toggleDoc(d.id)} />
                      <Trash2 size={14} color="var(--tm)" className="ptr" style={{ marginLeft: 16 }} />
                    </div>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", padding: "40px 20px", color: "var(--tm)" }}>No documents found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
