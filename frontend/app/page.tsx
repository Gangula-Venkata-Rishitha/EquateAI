"use client";

import Link from "next/link";
import { ArrowRight, FileText, Network, MessageSquare, Zap, Shield, Layers, ChevronDown } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white selection:bg-brand-100 selection:text-brand-900">
      <nav className="fixed top-0 left-0 right-0 h-16 md:h-20 flex items-center justify-between px-4 md:px-12 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-brand-600 rounded-xl flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-brand-200">
            E
          </div>
          <span className="font-bold text-xl tracking-tight text-gray-900">EquateAI</span>
        </div>
        <div className="flex items-center gap-8">
          <Link
            href="/upload"
            className="px-5 py-2.5 bg-gray-900 text-white rounded-full text-sm font-medium hover:bg-gray-800 transition-all hover:shadow-xl hover:-translate-y-0.5"
          >
            Launch App
          </Link>
        </div>
      </nav>

      <section className="relative pt-28 md:pt-40 pb-20 md:pb-32 px-4 md:px-6 overflow-hidden">
        <div className="max-w-6xl mx-auto text-center relative z-10">
          <div className="inline-block px-4 py-1.5 rounded-full bg-brand-50 text-brand-600 text-xs font-bold uppercase tracking-wider mb-6">
            Next-Gen Scientific Reasoning
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-7xl font-bold tracking-tight text-gray-900 mb-6 md:mb-8 leading-[0.95]">
            AI-Powered Scientific <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-brand-400">
              Equation Analysis
            </span>
          </h1>
          <p className="text-base md:text-xl text-gray-500 max-w-2xl mx-auto mb-8 md:mb-12 leading-relaxed px-2">
            Upload scientific documents to extract equations, analyze dependencies, build knowledge graphs, and
            interact with an AI reasoning assistant.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <Link
              href="/upload"
              className="px-8 py-4 bg-brand-600 text-white rounded-full text-lg font-semibold hover:bg-brand-700 transition-all hover:shadow-2xl hover:shadow-brand-200 hover:-translate-y-1 flex items-center gap-2"
            >
              Upload Document <ArrowRight size={20} />
            </Link>
          </div>
        </div>

        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full -z-10 pointer-events-none">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-brand-100/50 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-50/50 rounded-full blur-3xl" />
        </div>

        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gray-400">
          <span className="text-xs font-medium uppercase tracking-widest">Scroll to explore</span>
          <ChevronDown className="animate-bounce" size={20} />
        </div>
      </section>

      <section id="product" className="py-20 md:py-32 px-4 md:px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12 md:mb-20">
            <h2 className="text-2xl md:text-4xl font-bold text-gray-900 mb-3 md:mb-4">
              Powerful Scientific Workspace
            </h2>
            <p className="text-gray-500 text-sm md:text-lg">
              Everything you need to master complex mathematical models.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={FileText}
              title="Upload Documents"
              description="Extract equations from PDF and DOCX files with high precision using our neural parsing engine."
            />
            <FeatureCard
              icon={Network}
              title="Dependency Graphs"
              description="Visualize how variables and equations interact. Detect circular dependencies and conflicts instantly."
            />
            <FeatureCard
              icon={MessageSquare}
              title="AI Chat Assistant"
              description="Ask complex questions about your document's mathematical logic and get step-by-step reasoning."
            />
          </div>
        </div>
      </section>

      <section id="research" className="py-20 md:py-32 px-4 md:px-6 overflow-hidden">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center gap-10 md:gap-20">
            <div className="flex-1">
              <span className="text-brand-600 font-bold text-xs uppercase tracking-widest mb-4 block">
                Advanced Reasoning
              </span>
              <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-6 md:mb-8 leading-tight">
                Knowledge Graphs for <br />
                Deep Understanding
              </h2>
              <div className="space-y-6">
                <BenefitItem
                  icon={Zap}
                  title="Real-time Analysis"
                  text="Equations are parsed and analyzed as you upload, providing instant feedback."
                />
                <BenefitItem
                  icon={Shield}
                  title="Conflict Detection"
                  text="Automatically identify mathematical inconsistencies across multiple research papers."
                />
                <BenefitItem
                  icon={Layers}
                  title="Multi-format Support"
                  text="Seamlessly handle LaTeX, MathML, and handwritten scanned equations."
                />
              </div>
            </div>
            <div className="flex-1 relative">
              <div className="relative z-10 bg-white rounded-3xl shadow-2xl border border-gray-100 p-8 overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-br from-brand-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="relative z-10">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="w-12 h-12 rounded-2xl bg-brand-600 flex items-center justify-center text-white shadow-lg shadow-brand-200">
                      <Network size={24} />
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900">Interactive Graph</h3>
                      <p className="text-xs text-gray-500">Visualizing 124 dependencies</p>
                    </div>
                  </div>
                  <div className="mt-4 space-y-4">
                    <div className="relative h-56 overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900">
                      <svg
                        viewBox="0 0 300 200"
                        className="h-full w-full text-slate-400 transition-transform duration-500 group-hover:scale-105"
                      >
                        <defs>
                          <radialGradient id="edgeGlow" cx="50%" cy="50%" r="80%">
                            <stop offset="0%" stopColor="#4F46E5" stopOpacity="0.9" />
                            <stop offset="100%" stopColor="#1E293B" stopOpacity="0.1" />
                          </radialGradient>
                        </defs>

                        {/* Edges */}
                        <g
                          className="stroke-[url(#edgeGlow)] stroke-[1.4] transition-opacity duration-500 group-hover:opacity-100 opacity-70"
                        >
                          <line x1="150" y1="40" x2="70" y2="90" />
                          <line x1="150" y1="40" x2="230" y2="90" />
                          <line x1="70" y1="90" x2="60" y2="160" />
                          <line x1="70" y1="90" x2="120" y2="155" />
                          <line x1="230" y1="90" x2="185" y2="150" />
                          <line x1="230" y1="90" x2="255" y2="155" />
                        </g>

                        {/* Central node */}
                        <g className="transition-transform duration-500 group-hover:translate-y-[-2px]">
                          <circle cx="150" cy="40" r="18" className="fill-brand-500/90" />
                          <text
                            x="150"
                            y="44"
                            textAnchor="middle"
                            className="fill-white text-[9px] font-semibold"
                          >
                            F
                          </text>
                        </g>

                        {/* Child nodes */}
                        <g className="fill-slate-900">
                          <circle cx="70" cy="90" r="14" className="fill-slate-800 stroke-brand-400/60" />
                          <text
                            x="70"
                            y="94"
                            textAnchor="middle"
                            className="fill-slate-100 text-[8px] font-medium"
                          >
                            m
                          </text>

                          <circle cx="230" cy="90" r="14" className="fill-slate-800 stroke-brand-400/60" />
                          <text
                            x="230"
                            y="94"
                            textAnchor="middle"
                            className="fill-slate-100 text-[8px] font-medium"
                          >
                            a
                          </text>

                          <circle cx="60" cy="160" r="10" className="fill-slate-800 stroke-indigo-400/60" />
                          <text
                            x="60"
                            y="163"
                            textAnchor="middle"
                            className="fill-slate-100 text-[7px]"
                          >
                            work
                          </text>

                          <circle cx="120" cy="155" r="10" className="fill-slate-800 stroke-indigo-400/60" />
                          <text
                            x="120"
                            y="158"
                            textAnchor="middle"
                            className="fill-slate-100 text-[7px]"
                          >
                            energy
                          </text>

                          <circle cx="185" cy="150" r="10" className="fill-slate-800 stroke-emerald-400/60" />
                          <text
                            x="185"
                            y="153"
                            textAnchor="middle"
                            className="fill-slate-100 text-[7px]"
                          >
                            stress
                          </text>

                          <circle cx="255" cy="155" r="10" className="fill-slate-800 stroke-emerald-400/60" />
                          <text
                            x="255"
                            y="158"
                            textAnchor="middle"
                            className="fill-slate-100 text-[7px]"
                          >
                            power
                          </text>
                        </g>
                      </svg>

                      {/* Hover hint */}
                      <div className="pointer-events-none absolute inset-x-0 bottom-2 flex justify-center text-[10px] font-medium uppercase tracking-widest text-slate-400 opacity-0 transition-opacity duration-500 group-hover:opacity-100">
                        Hover to explore relationships
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-3 text-center text-[11px] text-gray-600">
                      <div className="rounded-xl bg-brand-50 px-2 py-2">
                        <p className="text-xs font-semibold text-brand-700">Central variable</p>
                        <p className="mt-1 text-[11px] text-brand-600">Force (F)</p>
                      </div>
                      <div className="rounded-xl bg-blue-50 px-2 py-2">
                        <p className="text-xs font-semibold text-blue-700">Dependents</p>
                        <p className="mt-1 text-[11px] text-blue-600">m, a</p>
                      </div>
                      <div className="rounded-xl bg-indigo-50 px-2 py-2">
                        <p className="text-xs font-semibold text-indigo-700">Derived metrics</p>
                        <p className="mt-1 text-[11px] text-indigo-600">work, energy…</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-brand-200 rounded-full blur-3xl opacity-30" />
              <div className="absolute -bottom-10 -left-10 w-60 h-60 bg-blue-200 rounded-full blur-3xl opacity-30" />
            </div>
          </div>
        </div>
      </section>

      <section id="pricing" className="py-20 px-6 border-t border-gray-100 bg-white">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
              E
            </div>
            <span className="font-bold text-lg tracking-tight text-gray-900">EquateAI</span>
          </div>
          <p className="text-sm text-gray-400">© {new Date().getFullYear()} EquateAI. All rights reserved.</p>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({
  icon: Icon,
  title,
  description,
}: {
  icon: typeof FileText;
  title: string;
  description: string;
}) {
  return (
    <div className="p-8 bg-white rounded-3xl border border-gray-100 shadow-premium hover:shadow-premium-hover transition-all duration-300 group">
      <div className="w-14 h-14 bg-brand-50 rounded-2xl flex items-center justify-center text-brand-600 mb-6 group-hover:bg-brand-600 group-hover:text-white transition-colors duration-300">
        <Icon size={28} />
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
      <p className="text-gray-500 leading-relaxed">{description}</p>
    </div>
  );
}

function BenefitItem({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Zap;
  title: string;
  text: string;
}) {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-brand-50 flex items-center justify-center text-brand-600">
        <Icon size={20} />
      </div>
      <div>
        <h4 className="font-bold text-gray-900 mb-1">{title}</h4>
        <p className="text-sm text-gray-500 leading-relaxed">{text}</p>
      </div>
    </div>
  );
}

