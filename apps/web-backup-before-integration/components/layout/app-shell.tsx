"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useState } from "react";
import { Bell, Bot, Menu, Plus, Search, Sparkles, X } from "lucide-react";
import { appNavigation } from "@/lib/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function SidebarContent({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <div className="flex h-full flex-col">
      <Link href="/dashboard" className="mb-8 flex items-center gap-3 px-2" onClick={onNavigate}>
        <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg shadow-indigo-500/20">
          <Bot className="h-5 w-5" />
        </span>
        <div>
          <p className="font-bold leading-tight">CustomModel</p>
          <p className="text-xs text-muted-foreground">Trainer</p>
        </div>
      </Link>

      <Button asChild className="mb-5 w-full justify-start">
        <Link href="/models/new" onClick={onNavigate}>
          <Plus className="h-4 w-4" />
          New model
        </Link>
      </Button>

      <nav className="space-y-1">
        {appNavigation.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-muted-foreground transition-all hover:bg-muted hover:text-foreground",
                isActive && "bg-secondary text-secondary-foreground shadow-sm"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-2xl border bg-gradient-to-br from-indigo-50 via-cyan-50 to-emerald-50 p-4">
        <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-white shadow-sm">
          <Sparkles className="h-5 w-5 text-primary" />
        </div>
        <p className="text-sm font-semibold">Feedback improvement</p>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">
          Store feedback for owner review before retraining a new version.
        </p>
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r bg-card/80 p-5 backdrop-blur-xl lg:block">
        <SidebarContent />
      </aside>

      {open ? (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-slate-950/40" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-80 max-w-[86vw] border-r bg-card p-5 shadow-2xl">
            <div className="mb-5 flex justify-end">
              <Button variant="ghost" size="icon" onClick={() => setOpen(false)} aria-label="Close navigation">
                <X className="h-5 w-5" />
              </Button>
            </div>
            <SidebarContent onNavigate={() => setOpen(false)} />
          </aside>
        </div>
      ) : null}

      <div className="lg:pl-72">
        <header className="sticky top-0 z-20 border-b bg-background/80 px-4 py-3 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setOpen(true)} aria-label="Open navigation">
              <Menu className="h-5 w-5" />
            </Button>
            <div className="relative hidden flex-1 sm:block">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input className="max-w-xl pl-9" placeholder="Search models, jobs, API keys..." />
            </div>
            <div className="ml-auto flex items-center gap-2">
              <Button variant="outline" size="icon" aria-label="Notifications">
                <Bell className="h-4 w-4" />
              </Button>
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-cyan-500 text-sm font-bold text-white">
                ST
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
  );
}
