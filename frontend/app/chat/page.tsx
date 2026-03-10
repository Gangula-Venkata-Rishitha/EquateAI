"use client";

import { useState, useRef, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";

function ChatContent() {
  const searchParams = useSearchParams();
  const documentIdParam = searchParams.get("documentId");
  const documentId = documentIdParam ? Number(documentIdParam) : undefined;
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = message.trim();
    if (!text || loading) return;
    setMessage("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    try {
      const res = await api.chat(sessionId, text, documentId);
      setMessages((m) => [...m, { role: "assistant", content: res.response }]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: e instanceof Error ? e.message : "Request failed" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[100dvh] flex-col bg-[var(--background)]">
      <header className="flex shrink-0 items-center border-b border-[var(--border)] px-4 py-3 md:px-6 md:py-4">
        <h1 className="text-base md:text-lg font-semibold">
          Chat {documentId ? `(document ${documentId})` : ""}
        </h1>
      </header>
      <div className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto px-4 py-4 md:px-6">
          {messages.length === 0 && (
            <p className="text-zinc-400">
              Ask anything about your document or equations. {documentId && "Context is set to this document."}
            </p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`mb-4 rounded-lg p-4 ${
                msg.role === "user"
                  ? "ml-8 bg-[var(--accent)]/20"
                  : "mr-8 bg-[var(--card)] border border-[var(--border)]"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
            </div>
          ))}
          {loading && <p className="text-zinc-400">Thinking…</p>}
          <div ref={bottomRef} />
        </div>
        <div className="shrink-0 border-t border-[var(--border)] p-3 md:p-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send();
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type a message…"
              className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
            />
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50 hover:bg-[var(--accent-muted)]"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center">Loading…</div>}>
      <ChatContent />
    </Suspense>
  );
}
