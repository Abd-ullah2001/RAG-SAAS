"use client";

import { Plus, Trash2, Code, Eye, EyeOff } from "lucide-react";
import { Btn, Badge, CodeBlk } from "@/components/ui/shared";
import { KEYS } from "@/lib/mock-data";

export default function ApiKeys() {
  const codeExample = `import { Ragsaas } from '@ragsaas/client';

const client = new Ragsaas({
  apiKey: process.env.RAGSAAS_API_KEY,
});

const response = await client.query({
  query: "What are the Q3 financial highlights?",
  collectionId: "default",
  stream: true
});

for await (const chunk of response) {
  process.stdout.write(chunk.text);
}`;

  return (
    <div>
      <div className="pghdr">
        <h1 className="pgtit">API Keys</h1>
        <p className="pgsub">Manage your secret keys for accessing the RAG API.</p>
      </div>

      <div className="sec">
        <div className="card mb24">
          <div className="fx jb ic p20" style={{ borderBottom: "1px solid var(--b)" }}>
            <div className="w6">Secret Keys</div>
            <Btn v="p" sm><Plus size={14} /> Create new secret key</Btn>
          </div>
          <div style={{ padding: "0 20px 20px" }}>
            <p className="xs tm mt16 mb16">Do not share your API key with others, or expose it in the browser or other client-side code.</p>
            <table className="tbl">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Secret Key</th>
                  <th>Created</th>
                  <th>Last Used</th>
                  <th style={{ textAlign: "right" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {KEYS.map(k => (
                  <tr key={k.id}>
                    <td className="w5">{k.name}</td>
                    <td>
                      <div className="kdisp" style={{ maxWidth: 200, display: "inline-block" }}>
                        {k.prefix}••••••••••••
                      </div>
                    </td>
                    <td className="tm">{k.created}</td>
                    <td className="tm">{k.used}</td>
                    <td>
                      <div className="fx jb ic gap10" style={{ justifyContent: "flex-end" }}>
                        {k.status === "active" ? <Badge t="ok">Active</Badge> : <Badge t="err">Revoked</Badge>}
                        <Trash2 size={14} color="var(--err)" className="ptr" style={{ marginLeft: 10, opacity: k.status === "active" ? 1 : 0.4 }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card p20">
          <div className="w6 mb12 fx ic gap8"><Code size={16} color="var(--cy)" /> Node.js Example</div>
          <p className="xs tm mb16">Install the SDK using <span className="mono">npm i @ragsaas/client</span> and authenticate with your API key.</p>
          <CodeBlk lang="typescript" code={codeExample} />
        </div>
      </div>
    </div>
  );
}
