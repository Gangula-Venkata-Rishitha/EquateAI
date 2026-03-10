"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

export default function EquationExplainPage() {
  const params = useParams();
  const docId = Number(params.id);
  const eqId = Number(params.eqId);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [rawText, setRawText] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (Number.isNaN(eqId)) return;
    api
      .explainEquation(eqId)
      .then((r) => {
        setRawText(r.raw_text);
        setExplanation(r.explanation);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Error"))
      .finally(() => setLoading(false));
  }, [eqId]);

  if (Number.isNaN(docId) || Number.isNaN(eqId)) return <p className="p-6">Invalid ID</p>;
  if (loading) return <p className="p-6 text-zinc-400">Loading…</p>;
  if (error) return <p className="p-6 text-red-400">{error}</p>;

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <header className="border-b border-[var(--border)] px-6 py-4">
        <Link href={`/documents/${docId}`} className="text-[var(--accent)] hover:underline">
          ← Document
        </Link>
      </header>
      <main className="mx-auto max-w-2xl px-6 py-8">
        <h1 className="mb-4 text-xl font-semibold">Equation</h1>
        <pre className="mb-6 rounded-lg border border-[var(--border)] bg-[var(--card)] p-4 font-mono text-sm">
          {rawText}
        </pre>
        <h2 className="mb-2 font-medium">Explanation (AI)</h2>
        <p className="text-zinc-300 whitespace-pre-wrap">{explanation}</p>
      </main>
    </div>
  );
}
