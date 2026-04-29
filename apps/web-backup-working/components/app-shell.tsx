"use client";

import { LogOut, Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { clearToken } from "@/lib/api";
import { Button } from "@/components/ui/button";

export function AppShell({ children }: { children: ReactNode }) {
  const router = useRouter();

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold text-slate-950">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-slate-950 text-white">
              <Sparkles className="h-4 w-4" />
            </span>
            CustomModel Trainer
          </Link>
          <Button variant="ghost" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}
