"use client";

import { Plus, ShieldCheck, Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { ModelCard } from "@/components/model-card";
import { LinkButton } from "@/components/ui/link-button";
import { Card } from "@/components/ui/card";
import { getMe, getToken, listModels } from "@/lib/api";
import type { CustomModel, User } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [models, setModels] = useState<CustomModel[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }

    async function loadDashboard() {
      try {
        const [me, modelItems] = await Promise.all([getMe(), listModels()]);
        setUser(me);
        setModels(modelItems);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboard();
  }, [router]);

  return (
    <AppShell>
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">Welcome{user?.full_name ? `, ${user.full_name}` : ""}</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Your models</h1>
        </div>
        <LinkButton href="/models/new">
          <Plus className="mr-2 h-4 w-4" />
          Create model
        </LinkButton>
      </div>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <StatCard label="Models" value={String(models.length)} />
        <StatCard label="Feedback review" value="Manual" />
        <StatCard label="API deploy" value="Planned" />
      </section>

      {error && <p className="mt-6 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</p>}

      {isLoading ? (
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {[1, 2].map((item) => (
            <div key={item} className="h-56 animate-pulse rounded-3xl bg-white" />
          ))}
        </div>
      ) : models.length === 0 ? (
        <Card className="mt-8 flex flex-col items-center py-16 text-center">
          <div className="grid h-14 w-14 place-items-center rounded-2xl bg-slate-100 text-slate-800">
            <Sparkles className="h-6 w-6" />
          </div>
          <h2 className="mt-5 text-xl font-semibold text-slate-950">Create your first model</h2>
          <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
            Start with the model category and metadata. In Phase 2, this model will accept datasets and show a Data Readiness Score.
          </p>
          <LinkButton href="/models/new" className="mt-6">Create model</LinkButton>
        </Card>
      ) : (
        <div className="mt-8 grid gap-5 md:grid-cols-2">
          {models.map((model) => (
            <ModelCard key={model.id} model={model} />
          ))}
        </div>
      )}
    </AppShell>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <ShieldCheck className="h-4 w-4 text-slate-400" />
      </div>
      <p className="mt-3 text-2xl font-bold text-slate-950">{value}</p>
    </Card>
  );
}
