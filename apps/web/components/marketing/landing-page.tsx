"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Bot, BrainCircuit, CheckCircle2, Database, Gauge, Lock, MessageSquareHeart, Rocket, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  { icon: Database, title: "Upload your data", copy: "Text pairs, image-caption manifests, and training files in a guided no-code flow." },
  { icon: Gauge, title: "Data readiness score", copy: "Catch missing fields, duplicates, weak examples, and quality issues before training." },
  { icon: BrainCircuit, title: "Fine-tune with LoRA", copy: "Prepare for efficient text and image model fine-tuning without overbuilding the MVP." },
  { icon: MessageSquareHeart, title: "Feedback improvement", copy: "Collect feedback safely, review it, then retrain a new version when you choose." },
  { icon: Rocket, title: "Deploy by API", copy: "Generate keys, monitor requests, and ship model endpoints to your users." },
  { icon: Lock, title: "Private by default", copy: "Owner-scoped workflows, privacy settings, and secure model version control." }
];

export function LandingPage() {
  return (
    <main className="overflow-hidden">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-4 py-5 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3 font-bold">
          <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg shadow-indigo-500/20">
            <Bot className="h-5 w-5" />
          </span>
          CustomModel Trainer
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-medium text-muted-foreground md:flex">
          <a href="#features" className="hover:text-foreground">Features</a>
          <a href="#flow" className="hover:text-foreground">Flow</a>
          <a href="#security" className="hover:text-foreground">Security</a>
        </nav>
        <div className="flex items-center gap-2">
          <Button asChild variant="ghost">
            <Link href="/login">Login</Link>
          </Button>
          <Button asChild>
            <Link href="/signup">Start free</Link>
          </Button>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl items-center gap-12 px-4 py-16 sm:px-6 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:py-24">
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-white/80 px-4 py-2 text-sm font-medium text-muted-foreground shadow-sm backdrop-blur">
            <Sparkles className="h-4 w-4 text-primary" />
            No-code training for text and image models
          </div>
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            Train custom AI models with your own data.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
            Create, clean, fine-tune, test, deploy, collect feedback, and version custom models from one beginner-friendly dashboard.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link href="/dashboard">
                View dashboard
                <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/models/new">Create model</Link>
            </Button>
          </div>
          <div className="mt-8 grid gap-3 text-sm text-muted-foreground sm:grid-cols-3">
            {['Text-to-Text', 'Text-to-Image', 'Reviewed feedback'].map((item) => (
              <div key={item} className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                {item}
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.55, delay: 0.1 }}
          className="relative"
        >
          <div className="absolute -inset-10 -z-10 rounded-full bg-gradient-to-br from-indigo-300/30 via-cyan-300/20 to-emerald-300/30 blur-3xl" />
          <div className="glass-panel rounded-[2rem] p-4">
            <div className="rounded-[1.5rem] border bg-card p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Current training job</p>
                  <h3 className="mt-1 text-xl font-bold">CX Answer Bot</h3>
                </div>
                <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">Training</span>
              </div>
              <div className="mt-6 space-y-4">
                {[
                  ['Data cleaned', '100%'],
                  ['LoRA fine-tuning', '68%'],
                  ['Evaluation', 'Pending'],
                  ['Version creation', 'Pending']
                ].map(([label, value], index) => (
                  <div key={label} className="rounded-2xl bg-muted p-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{label}</span>
                      <span className="text-muted-foreground">{value}</span>
                    </div>
                    <div className="mt-3 h-2 rounded-full bg-white">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: index === 0 ? '100%' : index === 1 ? '68%' : '12%' }}
                        transition={{ delay: 0.4 + index * 0.12, duration: 0.7 }}
                        className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="mb-10 max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">MVP experience</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Everything users need to move from data to deployed model.</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="h-full transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-200/70">
                  <CardContent className="p-6">
                    <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-secondary text-secondary-foreground">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h3 className="font-semibold">{feature.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{feature.copy}</p>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </section>

      <section id="flow" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] border bg-card p-6 shadow-sm sm:p-8">
          <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Product flow</p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight">Simple enough for beginners. Structured enough for production.</h2>
              <p className="mt-4 text-sm leading-6 text-muted-foreground">
                Feedback is stored for review first. Retraining only happens when the model owner approves data and clicks retrain.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {['Create model', 'Upload data', 'Readiness score', 'Train LoRA', 'Test playground', 'Deploy API', 'Collect feedback', 'Create new version'].map((step, index) => (
                <div key={step} className="rounded-2xl border bg-muted/50 p-4">
                  <span className="text-xs font-bold text-primary">0{index + 1}</span>
                  <p className="mt-2 font-semibold">{step}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="security" className="mx-auto max-w-7xl px-4 pb-20 sm:px-6 lg:px-8">
        <div className="rounded-[2rem] bg-slate-950 p-8 text-white sm:p-10">
          <div className="grid gap-8 lg:grid-cols-[1fr_0.8fr] lg:items-center">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-300">Security model</p>
              <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Private models, reviewed feedback, version rollback.</h2>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">
                Build the MVP with owner-scoped data, API keys, usage logs, and version history from day one.
              </p>
            </div>
            <Button asChild size="lg" variant="secondary">
              <Link href="/signup">
                Start building
                <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </main>
  );
}
