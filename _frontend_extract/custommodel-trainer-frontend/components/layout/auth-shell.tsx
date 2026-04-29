import Link from "next/link";
import type { ReactNode } from "react";
import { Bot } from "lucide-react";

export function AuthShell({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <main className="grid min-h-screen lg:grid-cols-[1.05fr_0.95fr]">
      <section className="hidden mesh-gradient p-10 lg:flex lg:flex-col lg:justify-between">
        <Link href="/" className="flex items-center gap-3 text-sm font-bold">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg shadow-indigo-500/20">
            <Bot className="h-5 w-5" />
          </span>
          CustomModel Trainer
        </Link>
        <div className="max-w-xl">
          <p className="mb-4 inline-flex rounded-full border bg-white/70 px-4 py-2 text-sm font-medium text-muted-foreground backdrop-blur">
            Train, test, deploy, improve
          </p>
          <h2 className="text-5xl font-bold tracking-tight">
            Build custom AI models without writing training code.
          </h2>
          <p className="mt-5 text-lg leading-8 text-muted-foreground">
            Upload your examples, review data quality, launch a training job, and improve from reviewed feedback.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3 text-sm">
          {['Data readiness', 'LoRA training', 'Version rollback'].map((item) => (
            <div key={item} className="rounded-2xl border bg-white/70 p-4 backdrop-blur">
              {item}
            </div>
          ))}
        </div>
      </section>
      <section className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md">
          <div className="mb-8 lg:hidden">
            <Link href="/" className="flex items-center gap-3 text-sm font-bold">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
                <Bot className="h-5 w-5" />
              </span>
              CustomModel Trainer
            </Link>
          </div>
          <div className="rounded-3xl border bg-card p-6 shadow-xl shadow-slate-200/60 sm:p-8">
            <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
            <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
            <div className="mt-8">{children}</div>
          </div>
        </div>
      </section>
    </main>
  );
}
