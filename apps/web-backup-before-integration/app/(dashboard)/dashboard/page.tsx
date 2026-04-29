"use client";

import Link from "next/link";
import { ArrowRight, CheckCircle2, Database, Plus, Rocket } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/shared/metric-card";
import { ModelCard } from "@/components/shared/model-card";
import { quickStats } from "@/lib/navigation";
import { models, usageSeries } from "@/lib/mock-data";
import { AnimatedSection } from "@/components/shared/animated-section";

export default function DashboardPage() {
  const maxUsage = Math.max(...usageSeries.map((item) => item.value));

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Dashboard"
        title="Build, train, deploy, and improve your models."
        description="Track model readiness, training progress, API usage, and reviewed feedback from one workspace."
        actions={
          <Button asChild>
            <Link href="/models/new"><Plus className="h-4 w-4" /> Create model</Link>
          </Button>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        {quickStats.map((stat, index) => <MetricCard key={stat.label} {...stat} delay={index * 0.05} />)}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <section>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Your models</h2>
            <Button variant="ghost" asChild>
              <Link href="/models/new">New model <ArrowRight className="h-4 w-4" /></Link>
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {models.map((model) => <ModelCard key={model.id} model={model} />)}
          </div>
        </section>

        <aside className="space-y-6">
          <AnimatedSection delay={0.1}>
            <Card>
              <CardHeader>
                <CardTitle>Usage this week</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex h-44 items-end gap-3">
                  {usageSeries.map((item) => (
                    <div key={item.label} className="flex flex-1 flex-col items-center gap-2">
                      <div className="flex h-36 w-full items-end rounded-full bg-muted p-1">
                        <div
                          className="w-full rounded-full bg-gradient-to-t from-indigo-500 to-cyan-400"
                          style={{ height: `${Math.max(18, (item.value / maxUsage) * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">{item.label}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </AnimatedSection>

          <Card className="bg-slate-950 text-white">
            <CardContent className="p-6">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10">
                <Rocket className="h-5 w-5 text-cyan-300" />
              </div>
              <h3 className="text-lg font-semibold">MVP next step</h3>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                Connect the data upload screen to S3-compatible storage and start calculating real readiness scores.
              </p>
              <Button asChild variant="secondary" className="mt-5 w-full">
                <Link href="/models/demo-cx-bot/data">Upload data</Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent activity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                { icon: CheckCircle2, label: "Feedback approved", detail: "12 examples added to retraining pool" },
                { icon: Database, label: "Dataset cleaned", detail: "48 duplicate rows flagged" },
                { icon: Rocket, label: "API key created", detail: "Production key ending in 42fd" }
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.label} className="flex gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-muted">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold">{item.label}</p>
                      <p className="text-xs text-muted-foreground">{item.detail}</p>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}
