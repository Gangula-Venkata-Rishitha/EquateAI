"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, type DocumentSummary, type Equation, type Conflict, type MissingVariable } from "@/lib/api";

export default function DocumentDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const router = useRouter();
  const [summary, setSummary] = useState<DocumentSummary | null>(null);
  const [equations, setEquations] = useState<Equation[]>([]);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [missingVars, setMissingVars] = useState<MissingVariable[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (Number.isNaN(id)) return;
    Promise.all([
      api.getDocumentSummary(id),
      api.getEquations(id),
      api.getConflicts(id),
      api.getMissingVariables(id),
    ])
      .then(([s, e, c, m]) => {
        setSummary(s);
        setEquations(e);
        setConflicts(c);
        setMissingVars(m);
      })
      .catch((e) => {
        const msg = e instanceof Error ? e.message : "Error";
        if (msg === "Failed to fetch") {
          setError("Could not reach the API. Make sure the backend is running on http://localhost:8000.");
        } else {
          setError(msg);
        }
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (Number.isNaN(id)) return <p className="p-6">Invalid document ID</p>;
  if (loading) return <p className="p-6 text-slate-600">Loading…</p>;
  if (error) {
    return (
      <div className="min-h-screen bg-[var(--background)]">
        <header className="border-b border-[var(--border)] px-6 py-4">
          <Link href="/documents" className="text-[var(--accent)] hover:underline">
            ← Documents
          </Link>
        </header>
        <main className="mx-auto max-w-3xl px-6 py-8">
        <h1 className="mb-4 text-xl font-semibold text-red-500">Unable to load document</h1>
        <p className="mb-4 text-sm text-slate-700">{error}</p>
        <p className="text-sm text-slate-600">
            If this document was deleted or never existed, you can go back to the{" "}
            <Link href="/documents" className="text-[var(--accent)] hover:underline">
              documents list
            </Link>
            .
          </p>
        </main>
      </div>
    );
  }
  if (!summary) return <p className="p-6">Document not found</p>;

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <header className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3 md:px-6 md:py-4">
        <Link
          href="/documents"
          className="text-xs md:text-sm text-[var(--accent)] hover:underline"
        >
          ← Documents
        </Link>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={async () => {
              const ok = window.confirm("Delete this document and all derived equations/graphs?");
              if (!ok) return;
              try {
                await api.deleteDocument(id);
                router.push("/documents");
              } catch (e) {
                alert(e instanceof Error ? e.message : "Failed to delete document");
              }
            }}
            className="rounded-lg border border-red-500/40 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-500/20"
          >
            Delete document
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6 md:px-6 md:py-8">
        <h1 className="mb-2 text-xl md:text-2xl font-semibold text-slate-900 break-words">
          {summary.filename}
        </h1>
        <p className="mb-4 md:mb-6 text-xs md:text-sm text-slate-600">
          Pages: {summary.page_count ?? "—"} · Equations: {summary.equation_count} · Undefined variables: {summary.undefined_variables_count}
        </p>
        <nav className="mb-6 md:mb-8 flex flex-wrap gap-3">
          <Link
            href={`/documents/${id}/graph`}
            className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm hover:border-[var(--accent)]"
          >
            Dependency graph
          </Link>
          <Link
            href={`/chat?documentId=${id}`}
            className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm hover:border-[var(--accent)]"
          >
            Chat
          </Link>
        </nav>
        <div className="grid gap-8 md:grid-cols-[2fr,1fr]">
          <section>
            <h2 className="mb-4 text-lg font-medium">Equations</h2>
            <ul className="space-y-4">
              {equations.map((eq) => {
                const isInConflict = conflicts.some((c) => c.equation_ids.includes(eq.equation_id));
                return (
                  <li
                    key={eq.equation_id}
                    className="rounded-lg border border-[var(--border)] bg-[var(--card)] p-4 text-sm"
                  >
                    <div className="mb-1 font-mono text-slate-900">{eq.raw_text}</div>
                    <div className="flex flex-wrap items-center gap-2 text-xs text-slate-600">
                      {eq.variables && eq.variables.length > 0 && (
                        <span>Variables: {eq.variables.join(", ")}</span>
                      )}
                      {isInConflict && (
                        <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-red-400">
                          Conflict
                        </span>
                      )}
                    </div>
                    <div className="mt-3 flex flex-wrap gap-3">
                      <Link
                        href={`/documents/${id}/equations/${eq.equation_id}`}
                        className="text-[var(--accent)] hover:underline"
                      >
                        Explain
                      </Link>
                      <button
                        type="button"
                        onClick={async () => {
                          try {
                            const res = await api.equationToText(eq.equation_id);
                            alert(res.explanation);
                          } catch (e) {
                            alert(e instanceof Error ? e.message : "Failed to convert to text");
                          }
                        }}
                        className="text-xs text-[var(--accent)] underline underline-offset-2 hover:text-[var(--accent-muted)]"
                      >
                        Quick explanation
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>
            {equations.length === 0 && <p className="text-zinc-400">No equations detected.</p>}
          </section>

          <aside className="space-y-6">
            <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <h2 className="mb-2 text-sm font-semibold">Conflicting equations</h2>
              {conflicts.length === 0 ? (
                <p className="text-xs text-slate-600">No conflicts detected.</p>
              ) : (
                <ul className="max-h-64 space-y-2 overflow-y-auto text-xs text-slate-800">
                  {conflicts.map((c) => (
                    <li key={c.id}>
                      <div className="font-medium text-red-600 break-words">
                        {c.variable}{" "}
                        <span className="ml-1 rounded-full bg-red-500/20 px-1.5 py-0.5 text-[10px] uppercase tracking-wide">
                          {c.conflict_type}
                        </span>
                      </div>
                      <div className="break-words text-slate-700">
                        Equations: {c.equation_ids.join(", ")}
                      </div>
                      {c.explanation && (
                        <div className="mt-0.5 break-words text-[11px] text-slate-600">
                          {c.explanation}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <h2 className="mb-2 text-sm font-semibold">Missing / undefined variables</h2>
              {missingVars.length === 0 ? (
                <p className="text-xs text-slate-600">None detected.</p>
              ) : (
                <ul className="max-h-64 space-y-1 overflow-y-auto text-xs text-amber-900">
                  {missingVars.map((v) => (
                    <li
                      key={v.name}
                      className="inline-block rounded-md bg-amber-100 px-2 py-0.5"
                    >
                      {v.name}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className="rounded-xl border border-[var(--border)] bg-[var(--card)] p-4">
              <h2 className="mb-2 text-sm font-semibold">Create equation from text</h2>
              <EquationFromTextForm />
            </section>
          </aside>
        </div>
      </main>
    </div>
  );
}

function EquationFromTextForm() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    const t = text.trim();
    if (!t || busy) return;
    setBusy(true);
    try {
      const res = await api.equationFromText(t);
      setResult(res.raw_text);
    } catch (e) {
      setResult(e instanceof Error ? e.message : "Conversion failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-2 text-xs">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="e.g. Force equals mass times acceleration"
        className="w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-2 text-xs outline-none ring-0 focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)]"
        rows={3}
      />
      <button
        type="button"
        onClick={submit}
        disabled={busy}
        className="rounded-lg bg-[var(--accent)] px-3 py-1.5 text-xs font-medium text-white disabled:opacity-50 hover:bg-[var(--accent-muted)]"
      >
        {busy ? "Converting…" : "Convert to equation"}
      </button>
      {result && (
        <div className="mt-1 rounded-md border border-[var(--border)] bg-black/20 px-2 py-1 font-mono">
          {result}
        </div>
      )}
    </div>
  );
}
