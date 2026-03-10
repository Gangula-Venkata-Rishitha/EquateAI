"use client";

import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { Menu, LayoutDashboard, Upload, Network, MessageSquare } from "lucide-react";
import { cn } from "@/lib/cn";
import { ReactNode, useState } from "react";

type AppShellProps = {
  children: ReactNode;
};

const workspaceLinks = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/documents", label: "Documents", icon: Network },
  { href: "/chat", label: "AI Assistant", icon: MessageSquare },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(() => {
    if (typeof window === "undefined") return true;
    return window.innerWidth >= 768;
  });

  const isWorkspace = pathname !== "/" && !pathname.startsWith("/login") && !pathname.startsWith("/signup");

  if (!isWorkspace) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen bg-[#F9FAFB] overflow-hidden font-sans">
      {sidebarOpen && (
        <aside className="w-64 border-r border-gray-200 bg-white flex flex-col z-30 max-md:fixed max-md:inset-y-0 max-md:left-0 max-md:shadow-xl">
          <div className="p-6 flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
              E
            </div>
            <span className="font-semibold text-lg tracking-tight">EquateAI</span>
          </div>
          <div className="flex-1 px-4 py-2 space-y-1">
            <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider px-3 mb-2">
              Workspace
            </div>
            {workspaceLinks.map((link) => {
              const Icon = link.icon;
              const active = pathname === link.href || pathname.startsWith(link.href + "/");
              return (
                <button
                  key={link.href}
                  onClick={() => router.push(link.href)}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 w-full text-left group",
                    active
                      ? "bg-brand-50 text-brand-600 font-medium"
                      : "text-gray-500 hover:bg-gray-100 hover:text-gray-900"
                  )}
                >
                  <Icon
                    size={18}
                    className={cn(
                      "transition-colors",
                      active ? "text-brand-600" : "text-gray-400 group-hover:text-gray-600"
                    )}
                  />
                  <span className="text-sm">{link.label}</span>
                  {active && <div className="ml-auto w-1 h-4 bg-brand-500 rounded-full" />}
                </button>
              );
            })}
          </div>
        </aside>
      )}

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <header className="h-14 border-b border-gray-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-4 md:px-6 z-20">
          <div className="flex items-center gap-2 md:gap-3">
            <button
              onClick={() => setSidebarOpen((v) => !v)}
              className="p-1.5 hover:bg-gray-100 rounded-md text-gray-500"
            >
              <Menu size={18} />
            </button>
            <div className="h-4 w-px bg-gray-200" />
            <span className="text-sm font-medium text-gray-900 max-sm:text-xs">Workspace</span>
          </div>
          <div className="flex items-center gap-2 md:gap-3">
            <Link
              href="/"
              className="rounded-full border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900"
            >
              Home
            </Link>
          </div>
        </header>

        <div className="flex-1 overflow-auto bg-[#F9FAFB]">{children}</div>
      </main>
    </div>
  );
}

