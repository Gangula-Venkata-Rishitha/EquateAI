const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export type DocumentSummary = {
  document_id: number;
  filename: string;
  page_count: number | null;
  equation_count: number;
  undefined_variables_count: number;
  status: string;
};

export type Equation = {
  equation_id: number;
  document_id: number;
  page: number | null;
  line_no: number | null;
  raw_text: string;
  confidence_score: number | null;
  variables: string[] | null;
  ast_json: Record<string, unknown> | null;
};

export type GraphNode = { id: string; label: string; type: string };
export type GraphEdge = { source: string; target: string; type: string };

export type DependencyGraph = { nodes: GraphNode[]; edges: GraphEdge[] };
export type KnowledgeGraph = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  triples?: { subject: string; predicate: string; object: string }[];
};

export type Conflict = {
  id: number;
  variable: string;
  conflict_type: string;
  equation_ids: number[];
  explanation?: string | null;
};

export type MissingVariable = { name: string };

export type DependencyIssues = {
  cycles: string[][];
};

type ApiOptions = {
  method?: string;
  headers?: HeadersInit;
  body?: object | FormData;
};

async function request<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { body, method, headers: optHeaders } = options;
  const headers: HeadersInit = { ...(optHeaders as Record<string, string>) };
  if (body && !(body instanceof FormData)) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }
  const fetchBody: BodyInit | undefined =
    body instanceof FormData ? body : body ? JSON.stringify(body) : undefined;
  const res = await fetch(`${API_BASE}${path}`, {
    method: method ?? "GET",
    headers: body instanceof FormData ? optHeaders : headers,
    body: fetchBody,
  });
  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const text = await res.text();
      if (text) {
        try {
          const json = JSON.parse(text) as { detail?: string };
          if (json.detail) {
            message = json.detail;
          } else {
            message = text;
          }
        } catch {
          message = text;
        }
      }
    } catch {
      // ignore
    }
    throw new Error(message);
  }
  const text = await res.text();
  if (!text) return undefined as T;
  try {
    return JSON.parse(text) as T;
  } catch {
    return text as T;
  }
}

export const api = {
  listDocuments: () =>
    request<{ document_id: number; filename: string; path: string; status: string }[]>("/documents"),

  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ document_id: number; filename: string; path: string; status: string }>(
      "/documents/upload",
      { method: "POST", body: form }
    );
  },

  processDocument: (documentId: number) =>
    request<{ document_id: number; status: string; equation_count: number; conflicts: unknown[] }>(
      `/documents/${documentId}/process`,
      { method: "POST" }
    ),

  getDocumentSummary: (documentId: number) =>
    request<DocumentSummary>(`/documents/${documentId}/summary`),

  getEquations: (documentId: number) =>
    request<Equation[]>(`/documents/${documentId}/equations`),

  getDependencyGraph: (documentId: number) =>
    request<DependencyGraph>(`/documents/${documentId}/dependency-graph`),

  getKnowledgeGraph: (documentId: number) =>
    request<KnowledgeGraph>(`/documents/${documentId}/knowledge-graph`),

  getConflicts: (documentId: number) =>
    request<Conflict[]>(`/documents/${documentId}/conflicts`),

  getMissingVariables: (documentId: number) =>
    request<MissingVariable[]>(`/documents/${documentId}/missing-variables`),

  getDependencyIssues: (documentId: number) =>
    request<DependencyIssues>(`/documents/${documentId}/dependency-issues`),

  explainEquation: (equationId: number, context?: string) =>
    request<{ equation_id: number; raw_text: string; explanation: string }>(
      `/equations/${equationId}/explain`,
      { method: "POST", body: context ? { equation_id: equationId, context } : {} }
    ),

  equationToText: (equationId: number) =>
    request<{ equation_id: number; raw_text: string; explanation: string; readable: boolean }>(
      `/equations/${equationId}/to-text`,
      { method: "POST" }
    ),

  equationFromText: (text: string) =>
    request<{ raw_text: string }>(`/equations/from-text`, {
      method: "POST",
      body: { text },
    }),

  deleteDocument: (documentId: number) =>
    request<{ status: string }>(`/documents/${documentId}`, { method: "DELETE" }),

  chat: (sessionId: string, message: string, documentId?: number) =>
    request<{ response: string; session_id: string }>("/chat", {
      method: "POST",
      body: { session_id: sessionId, message, document_id: documentId },
    }),
};
