"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<{ document_id: number; filename: string; status: string }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listDocuments()
      .then(setDocs)
      .catch((e) => setError(e instanceof Error ? e.message : "Error"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <main className="mx-auto max-w-3xl px-6 py-12">
        <h1 className="mb-6 text-2xl font-semibold">Documents</h1>
        {loading && <p className="text-zinc-400">Loading…</p>}
        {error && <p className="text-red-400">{error}</p>}
        {!loading && !error && docs.length === 0 && (
          <p className="text-zinc-400">No documents yet. <Link href="/upload" className="text-[var(--accent)]">Upload one</Link>.</p>
        )}
        {!loading && docs.length > 0 && (
          <ul className="space-y-2">
            {docs.map((d) => (
              <li key={d.document_id}>
                <Link
                  href={`/documents/${d.document_id}`}
                  className="block rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3 transition hover:border-[var(--accent)]"
                >
                  <span className="font-medium">{d.filename}</span>
                  <span className="ml-2 text-sm text-zinc-400">({d.status})</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
