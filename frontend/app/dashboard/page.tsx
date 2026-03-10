"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { FileText, Upload, Network, MessageSquare, AlertCircle } from "lucide-react";

type DashboardDoc = { document_id: number; filename: string; status: string; path: string };

export default function DashboardPage() {
  const [docs, setDocs] = useState<DashboardDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listDocuments()
      .then((data) => setDocs(data.slice(0, 5)))
      .catch((e) => setError(e instanceof Error ? e.message : "Error loading dashboard"))
      .finally(() => setLoading(false));
  }, []);

  const totalDocs = docs.length;
  const processingDocs = docs.filter((d) => d.status !== "processed").length;

  return (
    <div className="h-full bg-[#F9FAFB]">
      <div className="mx-auto flex h-full max-w-6xl flex-col gap-8 px-8 py-8">
        <header className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">
            Quick overview of your scientific documents, equation graphs, and AI activity.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-widest text-gray-400">
                  Documents
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">{totalDocs}</p>
              </div>
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
                <FileText size={18} />
              </div>
            </div>
            <p className="mt-3 text-xs text-gray-500">
              Recently processed documents available for graph analysis and chat.
            </p>
          </div>

          <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-widest text-gray-400">
                  In Progress
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">{processingDocs}</p>
              </div>
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
                <AlertCircle size={18} />
              </div>
            </div>
            <p className="mt-3 text-xs text-gray-500">
              Uploads still being processed by the equation pipeline.
            </p>
          </div>

          <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-widest text-gray-400">
                  Quick Actions
                </p>
                <p className="mt-2 text-sm text-gray-700">
                  Jump into the most common EquateAI workflows.
                </p>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <Link
                href="/upload"
                className="inline-flex items-center gap-2 rounded-full bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700"
              >
                <Upload size={14} />
                Upload document
              </Link>
              <Link
                href="/documents"
                className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200"
              >
                <Network size={14} />
                View documents
              </Link>
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-200"
              >
                <MessageSquare size={14} />
                Ask AI
              </Link>
            </div>
          </div>
        </section>

        <section className="grid gap-6 md:grid-cols-[minmax(0,2fr),minmax(0,1.2fr)]">
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold text-gray-900">Recent documents</h2>
                <p className="text-xs text-gray-500">
                  The last few documents you uploaded to EquateAI.
                </p>
              </div>
              <Link href="/documents" className="text-xs font-medium text-brand-600 hover:underline">
                View all
              </Link>
            </div>
            {loading && <p className="text-xs text-gray-400">Loading documents…</p>}
            {error && <p className="text-xs text-red-500">{error}</p>}
            {!loading && !error && docs.length === 0 && (
              <p className="text-xs text-gray-400">
                No documents yet.{" "}
                <Link href="/upload" className="text-brand-600 hover:underline">
                  Upload your first one.
                </Link>
              </p>
            )}
            {!loading && !error && docs.length > 0 && (
              <ul className="space-y-3">
                {docs.map((d) => (
                  <li key={d.document_id}>
                    <Link
                      href={`/documents/${d.document_id}`}
                      className="flex items-center justify-between rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm hover:bg-white hover:border-brand-200"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-gray-400">
                          <FileText size={16} />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 truncate max-w-xs">
                            {d.filename}
                          </p>
                          <p className="text-[11px] text-gray-500">{d.status}</p>
                        </div>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="space-y-4">
            <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
              <h2 className="mb-2 text-sm font-semibold text-gray-900">Graph insights</h2>
              <p className="text-xs text-gray-500">
                Once documents are processed, open a document and navigate to its dependency or
                knowledge graphs for detailed structure.
              </p>
              <div className="mt-4 grid grid-cols-3 gap-3 text-center text-[11px] text-gray-600">
                <div className="rounded-xl bg-brand-50 px-2 py-3">
                  <p className="text-xs font-semibold text-brand-700">Centrality</p>
                  <p className="mt-1 text-[11px] text-brand-600">Key variables ranking</p>
                </div>
                <div className="rounded-xl bg-blue-50 px-2 py-3">
                  <p className="text-xs font-semibold text-blue-700">Conflicts</p>
                  <p className="mt-1 text-[11px] text-blue-600">Equation inconsistencies</p>
                </div>
                <div className="rounded-xl bg-indigo-50 px-2 py-3">
                  <p className="text-xs font-semibold text-indigo-700">Influence</p>
                  <p className="mt-1 text-[11px] text-indigo-600">Propagation depth</p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
              <h2 className="mb-2 text-sm font-semibold text-gray-900">Tips</h2>
              <ul className="space-y-2 text-xs text-gray-500">
                <li>Use the Upload page to ingest PDFs or DOCX research papers.</li>
                <li>
                  After processing, open a document to inspect equations, conflicts, and missing
                  variables.
                </li>
                <li>
                  Use the Chat page with a selected document to get equation explanations and proofs.
                </li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

