"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ReactFlow,
  ReactFlowProvider,
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  MiniMap,
  useReactFlow,
  NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import ELK from "elkjs/lib/elk.bundled.js";
import katex from "katex";
import "katex/dist/katex.min.css";
import {
  api,
  type DependencyGraph,
  type GraphNode,
  type GraphEdge,
  type Conflict,
  type MissingVariable,
  type DependencyIssues,
} from "@/lib/api";

const elk = new ELK();

type NodeKind = "equation" | "variable" | "concept" | "constant";

function getNodeKind(n: GraphNode): NodeKind {
  if (n.type === "equation") return "equation";
  if (n.type === "concept") return "concept";
  if (n.type === "constant") return "constant";
  return "variable";
}

type CardNodeData = {
  label: string;
  kind: NodeKind;
};

function EquationNode({ data }: { data: CardNodeData }) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(data.label, {
        throwOnError: false,
      });
    } catch {
      return data.label;
    }
  }, [data.label]);
  return (
    <div className="rf-node-card rf-node-equation">
      <div
        className="katex-block"
        dangerouslySetInnerHTML={{ __html: html }}
      />
      <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
        Equation
      </div>
    </div>
  );
}

function VariableNode({ data }: { data: CardNodeData }) {
  return (
    <div className="rf-node-card rf-node-variable">
      <div>{data.label}</div>
      <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
        Variable
      </div>
    </div>
  );
}

function ConceptNode({ data }: { data: CardNodeData }) {
  return (
    <div className="rf-node-card rf-node-concept">
      <div>{data.label}</div>
      <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
        Concept
      </div>
    </div>
  );
}

function ConstantNode({ data }: { data: CardNodeData }) {
  return (
    <div className="rf-node-card rf-node-constant">
      <div>{data.label}</div>
      <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
        Constant
      </div>
    </div>
  );
}

const nodeTypes = {
  equation: EquationNode,
  variable: VariableNode,
  concept: ConceptNode,
  constant: ConstantNode,
};

type Filters = {
  equation: boolean;
  variable: boolean;
  concept: boolean;
  constant: boolean;
};

async function layoutWithElk(graph: DependencyGraph, filters: Filters) {
  const filteredNodes = graph.nodes.filter((n) => filters[getNodeKind(n)]);
  const nodeIds = new Set(filteredNodes.map((n) => n.id));
  const filteredEdges = graph.edges.filter(
    (e) => nodeIds.has(e.source) && nodeIds.has(e.target),
  );

  const elkGraph = {
    id: "root",
    layoutOptions: {
      // Use a tree-style layout so dependencies appear in clear levels
      "elk.algorithm": "mrtree",
      "elk.direction": "DOWN",
      "elk.spacing.nodeNode": "80",
      "elk.spacing.edgeEdge": "40",
      "elk.spacing.edgeNode": "40",
    },
    children: filteredNodes.map((n) => ({
      id: n.id,
      width: 220,
      height: 80,
    })),
    edges: filteredEdges.map((e) => ({
      id: `${e.source}-${e.target}`,
      sources: [e.source],
      targets: [e.target],
    })),
  };

  const res = await elk.layout(elkGraph as any);
  const positions = new Map<string, { x: number; y: number }>();
  res.children?.forEach((c: any) => {
    positions.set(c.id, { x: c.x ?? 0, y: c.y ?? 0 });
  });

  const nodes: Node<CardNodeData>[] = filteredNodes.map((n) => {
    const kind = getNodeKind(n);
    const pos = positions.get(n.id) ?? { x: 0, y: 0 };
    return {
      id: n.id,
      type: kind,
      position: pos,
      data: {
        label: n.label.length > 80 ? n.label.slice(0, 77) + "…" : n.label,
        kind,
      },
    };
  });

  const edges: Edge[] = filteredEdges.map((e) => ({
    source: e.source,
    target: e.target,
    type: "straight",
    markerEnd: { type: MarkerType.ArrowClosed },
    data: { kind: e.type },
  }));

  return { nodes, edges };
}

function DependencyGraphInner() {
  const params = useParams();
  const id = Number(params.id);
  const [graph, setGraph] = useState<DependencyGraph | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<Filters>({
    equation: true,
    variable: true,
    concept: true,
    constant: true,
  });
  const [search, setSearch] = useState("");
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [missingVars, setMissingVars] = useState<MissingVariable[]>([]);
  const [issues, setIssues] = useState<DependencyIssues | null>(null);

  useEffect(() => {
    if (Number.isNaN(id)) return;
    Promise.all([
      api.getDependencyGraph(id),
      api.getConflicts(id),
      api.getMissingVariables(id),
      api.getDependencyIssues(id),
    ])
      .then(([g, c, m, d]) => {
        setGraph(g);
        setConflicts(c);
        setMissingVars(m);
        setIssues(d);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Error"))
      .finally(() => setLoading(false));
  }, [id]);

  const [nodes, setNodes, onNodesChange] = useNodesState<Node<CardNodeData>>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [isLayingOut, setIsLayingOut] = useState(false);
  const reactFlow = useReactFlow();

  useEffect(() => {
    if (!graph) return;
    let cancelled = false;
    setIsLayingOut(true);
    layoutWithElk(graph, filters)
      .then(({ nodes: n, edges: e }) => {
        if (cancelled) return;
        setNodes(n);
        setEdges(e);
        // fitView is called after initial layout
        setTimeout(() => {
          try {
            reactFlow.fitView({ padding: 0.2, duration: 200 });
          } catch {
            // ignore
          }
        }, 0);
      })
      .finally(() => {
        if (!cancelled) setIsLayingOut(false);
      });
    return () => {
      cancelled = true;
    };
  }, [graph, filters, setNodes, setEdges, reactFlow]);

  const handleNodeMouseEnter: NodeMouseHandler = (_, node) => {
    setHoveredId(node.id);
  };
  const handleNodeMouseLeave: NodeMouseHandler = () => {
    setHoveredId(null);
  };

  const handleNodeClick: NodeMouseHandler = (_, node) => {
    setSelectedId(node.id);
  };

  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedId),
    [nodes, selectedId],
  );

  const legend = (
    <div className="rounded-xl border border-slate-200 bg-white/90 px-3 py-2 text-xs shadow-sm">
      <div className="mb-1 font-medium text-slate-700">Legend</div>
      <div className="flex flex-wrap gap-2">
        <span className="inline-flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-[var(--equation-node)] border border-slate-300" />
          Equation
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-[var(--variable-node)] border border-slate-300" />
          Variable
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-[var(--concept-node)] border border-slate-300" />
          Concept
        </span>
        <span className="inline-flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-[var(--constant-node)] border border-slate-300" />
          Constant
        </span>
      </div>
    </div>
  );

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!search.trim()) return;
    const term = search.trim().toLowerCase();
    const found = nodes.find((n) => n.data.label.toLowerCase().includes(term));
    if (found) {
      setSelectedId(found.id);
      reactFlow.setCenter(found.position.x, found.position.y, {
        zoom: 1.2,
        duration: 200,
      });
    }
  };

  const cycleEdgeKeys = new Set<string>();
  if (issues?.cycles) {
    issues.cycles.forEach((cycle) => {
      for (let i = 0; i < cycle.length; i += 1) {
        const a = cycle[i];
        const b = cycle[(i + 1) % cycle.length];
        cycleEdgeKeys.add(`${a}->${b}`);
      }
    });
  }

  const filteredEdges: Edge[] = edges.map((e, idx) => {
    const isHoverRelated =
      hoveredId &&
      (e.source === hoveredId || e.target === hoveredId || e.id === hoveredId);
    const isSelectedRelated =
      selectedId &&
      (e.source === selectedId || e.target === selectedId || e.id === selectedId);
    const inCycle = cycleEdgeKeys.has(`${e.source}->${e.target}`);
    const active = isHoverRelated || isSelectedRelated || inCycle;
    const kind = (e.data as any)?.kind as string | undefined;
    const baseColor =
      kind === "defines"
        ? "var(--edge-defines)"
        : kind === "depends_on"
        ? "var(--edge-depends)"
        : "var(--edge-default)";
    const isIncidentToSelected =
      !!selectedId && (e.source === selectedId || e.target === selectedId);
    const strokeColor = isIncidentToSelected ? "var(--accent)" : baseColor;
    const strokeWidth = isIncidentToSelected ? 2.5 : 1.6;

    return {
      ...e,
      // Fully unique id per edge to avoid React key collisions
      id: `${e.source}-${e.target}-${(e.data as any)?.kind ?? e.type ?? "edge"}-${idx}`,
      style: {
        stroke: strokeColor,
        strokeWidth,
        opacity: active ? 1 : hoveredId || selectedId ? 0.35 : 0.9,
      },
      animated: !!active,
    } as Edge;
  });

  const conflictNodeIds = new Set<string>();
  conflicts.forEach((c) => {
    c.equation_ids.forEach((id) => conflictNodeIds.add(`eq_${id}`));
  });
  const missingVarSet = new Set(missingVars.map((v) => v.name));

  const decoratedNodes = nodes.map((n) => {
    const isHover = hoveredId === n.id;
    const isSelected = selectedId === n.id;
    const neighbors = new Set<string>();
    if (hoveredId || selectedId) {
      filteredEdges.forEach((e) => {
        if (e.source === (hoveredId || selectedId)) neighbors.add(e.target);
        if (e.target === (hoveredId || selectedId)) neighbors.add(e.source);
      });
    }
    const shouldDim =
      (hoveredId || selectedId) &&
      !isHover &&
      !isSelected &&
      !neighbors.has(n.id);
    const isConflict = conflictNodeIds.has(n.id);
    const isMissing = missingVarSet.has(n.id);
    const extra =
      isConflict && isMissing
        ? " ring-2 ring-red-400"
        : isConflict
        ? " ring-2 ring-red-400"
        : isMissing
        ? " ring-2 ring-amber-400"
        : "";
    return {
      ...n,
      className: `${shouldDim ? "rf-node-dimmed" : ""}${extra}`,
      // Ensure tree levels render cleanly with consistent handles
      sourcePosition: "bottom",
      targetPosition: "top",
    } as Node<CardNodeData>;
  });

  if (Number.isNaN(id)) return <p className="p-6">Invalid document ID</p>;
  if (loading) return <p className="p-6 text-slate-600">Loading graph…</p>;
  if (error) return <p className="p-6 text-red-600">{error}</p>;

  return (
    <div className="flex h-screen flex-col bg-[#fafafa]">
      <header className="flex shrink-0 items-center border-b border-slate-200 px-6 py-4 bg-white/80 backdrop-blur">
        <Link href={`/documents/${id}`} className="text-[var(--accent)] hover:underline">
          ← Document
        </Link>
        <h1 className="ml-4 text-lg font-semibold text-slate-900">Dependency graph</h1>
      </header>
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar */}
        <aside className="w-64 border-r border-slate-200 bg-white/80 px-4 py-4">
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Graph filters
          </h2>
          <div className="space-y-2 text-sm text-slate-700">
            {(["equation", "variable", "concept", "constant"] as NodeKind[]).map((k) => (
              <label key={k} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="h-3.5 w-3.5 rounded border-slate-300 text-[var(--accent)]"
                  checked={filters[k]}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      [k]: e.target.checked,
                    }))
                  }
                />
                <span className="capitalize">{k}</span>
              </label>
            ))}
          </div>

          <div className="mt-6">
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
              Search
            </h2>
            <form onSubmit={handleSearchSubmit} className="space-y-2 text-sm">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search node…"
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm outline-none ring-0 focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)]"
              />
              <button
                type="submit"
                className="w-full rounded-lg bg-[var(--accent)] px-3 py-1.5 text-xs font-medium text-white hover:bg-[var(--accent-muted)]"
              >
                Go to node
              </button>
            </form>
          </div>

          <div className="mt-6">{legend}</div>
        </aside>

        {/* Graph canvas */}
        <main className="graph-container relative flex-1">
          <ReactFlow
            nodes={decoratedNodes}
            edges={filteredEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            nodeTypes={nodeTypes}
            className="h-full w-full"
            onNodeMouseEnter={handleNodeMouseEnter}
            onNodeMouseLeave={handleNodeMouseLeave}
            onNodeClick={handleNodeClick}
          >
            <Background
              gap={24}
              size={1}
              color="#e5e7eb"
            />
            <MiniMap
              nodeColor={(n) => {
                const kind = (n.data as CardNodeData)?.kind;
                switch (kind) {
                  case "equation":
                    return "#4f46e5";
                  case "concept":
                    return "#7c3aed";
                  case "constant":
                    return "#f97316";
                  default:
                    return "#0f172a";
                }
              }}
              maskColor="rgba(248, 250, 252, 0.8)"
            />
            <Controls
              position="top-left"
              style={{ left: 12, top: 12, borderRadius: 9999, boxShadow: "0 4px 12px rgba(15,23,42,0.08)" }}
              showInteractive={false}
            />
          </ReactFlow>
          {isLayingOut && (
            <div className="pointer-events-none absolute left-1/2 top-4 -translate-x-1/2 rounded-full bg-white/80 px-3 py-1 text-xs text-slate-500 shadow-sm">
              Optimizing layout…
            </div>
          )}
        </main>

        {/* Details panel */}
        <aside className="w-72 border-l border-slate-200 bg-white/90 px-4 py-4">
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Node details
          </h2>
          {selectedNode ? (
            <div className="space-y-3 text-sm text-slate-800">
              <div>
                <div className="text-xs font-medium text-slate-500">Name</div>
                <div className="mt-0.5 break-words">{selectedNode.data.label}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-slate-500">Type</div>
                <div className="mt-0.5 capitalize">
                  {(selectedNode.data as CardNodeData).kind}
                </div>
              </div>
              {graph && (
                <>
                  <div>
                    <div className="text-xs font-medium text-slate-500">Outgoing</div>
                    <ul className="mt-1 space-y-1 text-xs text-slate-600">
                      {graph.edges
                        .filter((e) => e.source === selectedNode.id)
                        .map((e) => (
                          <li key={`${e.source}-${e.target}`}>
                            → {e.target}{" "}
                            <span className="rounded-full bg-slate-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide">
                              {e.type}
                            </span>
                          </li>
                        ))}
                      {graph.edges.filter((e) => e.source === selectedNode.id).length === 0 && (
                        <li className="text-slate-400">None</li>
                      )}
                    </ul>
                  </div>
                  <div>
                    <div className="text-xs font-medium text-slate-500">Incoming</div>
                    <ul className="mt-1 space-y-1 text-xs text-slate-600">
                      {graph.edges
                        .filter((e) => e.target === selectedNode.id)
                        .map((e) => (
                          <li key={`${e.source}-${e.target}`}>
                            {e.source} →
                            <span className="ml-1 rounded-full bg-slate-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide">
                              {e.type}
                            </span>
                          </li>
                        ))}
                      {graph.edges.filter((e) => e.target === selectedNode.id).length === 0 && (
                        <li className="text-slate-400">None</li>
                      )}
                    </ul>
                  </div>
                </>
              )}
            </div>
          ) : (
            <p className="text-sm text-slate-400">Click a node to see its details.</p>
          )}
        </aside>
      </div>
    </div>
  );
}

export default function DependencyGraphPage() {
  return (
    <ReactFlowProvider>
      <DependencyGraphInner />
    </ReactFlowProvider>
  );
}
