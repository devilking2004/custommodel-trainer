"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { ArrowRight, Database, Rocket, Sparkles } from "lucide-react";
import Link from "next/link";

export function LandingHero() {
  return (
    <section className="relative overflow-hidden px-6 py-20 sm:py-28">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,rgba(99,102,241,0.20),transparent_34%),radial-gradient(circle_at_top_right,rgba(14,165,233,0.16),transparent_28%)]" />
      <motion.div
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mx-auto max-w-6xl"
      >
        <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 shadow-sm">
          <Sparkles className="h-4 w-4" />
          No-code custom AI model training
        </div>

        <div className="mt-8 grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div>
            <h1 className="max-w-4xl text-5xl font-bold tracking-tight text-slate-950 sm:text-6xl">
              Train, test, deploy, and improve custom AI models from your own data.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              CustomModel Trainer starts with two practical model categories: Text-to-Text and Text-to-Image. Upload examples, validate data, fine-tune, test in a playground, and deploy by API.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link
                href="/signup"
                className="inline-flex h-12 items-center justify-center rounded-xl bg-slate-950 px-6 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
              >
                Start building <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex h-12 items-center justify-center rounded-xl border border-slate-200 bg-white px-6 text-sm font-semibold text-slate-950 transition hover:bg-slate-50"
              >
                Sign in
              </Link>
            </div>
          </div>

          <div className="rounded-[2rem] border border-slate-200 bg-white p-4 shadow-xl shadow-slate-200/60">
            <div className="rounded-[1.5rem] bg-slate-950 p-5 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-300">Data Readiness Score</p>
                  <p className="mt-1 text-4xl font-bold">86%</p>
                </div>
                <Database className="h-9 w-9 text-slate-300" />
              </div>
              <div className="mt-6 h-3 rounded-full bg-white/10">
                <div className="h-3 w-[86%] rounded-full bg-white" />
              </div>
              <div className="mt-6 grid grid-cols-2 gap-3">
                <Metric label="Clean rows" value="12,480" />
                <Metric label="Warnings" value="18" />
                <Metric label="Queued job" value="LoRA" />
                <Metric label="Deploy" value="API" />
              </div>
            </div>
            <div className="mt-4 grid gap-3 rounded-[1.5rem] bg-slate-50 p-4">
              <PipelineStep icon={<Database className="h-4 w-4" />} title="Upload data" />
              <PipelineStep icon={<Sparkles className="h-4 w-4" />} title="AI cleaning assistant" />
              <PipelineStep icon={<Rocket className="h-4 w-4" />} title="Train and version model" />
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white/10 p-3">
      <p className="text-xs text-slate-300">{label}</p>
      <p className="mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}

function PipelineStep({ icon, title }: { icon: ReactNode; title: string }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl bg-white p-3 text-sm font-medium text-slate-700 shadow-sm">
      <span className="grid h-8 w-8 place-items-center rounded-xl bg-slate-100 text-slate-700">{icon}</span>
      {title}
    </div>
  );
}
