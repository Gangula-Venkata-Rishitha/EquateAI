"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      const doc = await api.uploadDocument(file);
      setUploading(false);
      setProcessing(true);
      await api.processDocument(doc.document_id);
      setProcessing(false);
      router.push(`/documents/${doc.document_id}`);
    } catch (e) {
      setUploading(false);
      setProcessing(false);
      setError(e instanceof Error ? e.message : "Upload failed");
    }
  };

  return (
    <div className="min-h-screen bg-[var(--background)]">
      <main className="mx-auto max-w-xl px-6 py-12">
        <h1 className="mb-6 text-2xl font-semibold">Upload document</h1>
        <p className="mb-4 text-zinc-400">Supported: PDF, DOCX</p>
        <div className="mb-4">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm file:mr-4 file:rounded file:border-0 file:bg-[var(--accent)] file:px-4 file:py-2 file:text-white"
          />
        </div>
        {error && <p className="mb-4 text-red-400">{error}</p>}
        <button
          onClick={handleUpload}
          disabled={!file || uploading || processing}
          className="rounded-lg bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-white disabled:opacity-50 hover:bg-[var(--accent-muted)] disabled:hover:bg-[var(--accent)]"
        >
          {uploading ? "Uploading…" : processing ? "Processing…" : "Upload & process"}
        </button>
      </main>
    </div>
  );
}
