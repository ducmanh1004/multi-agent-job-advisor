"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BriefcaseBusiness,
  FilePenLine,
  FileText,
  Gauge,
  GitBranch,
  Layers3,
  LogIn,
  Map,
  Network,
  Search,
  Upload,
  Waypoints
} from "lucide-react";

import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/upload-cv", label: "Upload CV", icon: Upload },
  { href: "/job-sources", label: "Job Sources", icon: Network },
  { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/match", label: "Match", icon: Search },
  { href: "/skill-gap", label: "Skill Gap", icon: GitBranch },
  { href: "/roadmap", label: "Roadmap", icon: Map },
  { href: "/cv-improve", label: "CV Improve", icon: FilePenLine },
  { href: "/interview", label: "Interview", icon: FileText },
  { href: "/agent-trace", label: "Agent Trace", icon: Activity }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-border bg-panel lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-border px-5">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-white">
            <Waypoints size={19} />
          </div>
          <div>
            <div className="text-sm font-semibold">Job Advisor</div>
            <div className="text-xs text-muted">Vietnam IT/AI market</div>
          </div>
        </div>
        <nav className="space-y-1 p-3">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-10 items-center gap-3 rounded-md px-3 text-sm text-muted transition hover:bg-slate-100 hover:text-foreground",
                  active && "bg-slate-100 font-medium text-foreground"
                )}
              >
                <Icon size={17} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-border bg-panel/95 px-4 backdrop-blur lg:px-8">
          <div className="flex items-center gap-3 lg:hidden">
            <Layers3 size={20} />
            <span className="text-sm font-semibold">Job Advisor</span>
          </div>
          <div className="hidden text-sm text-muted lg:block">Multi-Agent Job Discovery & CV Advisor</div>
          <Link className="flex h-9 items-center gap-2 rounded-md border border-border px-3 text-sm text-foreground" href="/login">
            <LogIn size={16} />
            Login
          </Link>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-6 lg:px-8">{children}</main>
      </div>
    </div>
  );
}

