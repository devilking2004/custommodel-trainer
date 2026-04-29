"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
    ArrowRight,
    Bot,
    CheckCircle2,
    Database,
    Plus,
    Rocket,
    Trash2,
    TrendingUp,
} from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/shared/metric-card";
import { ModelCard } from "@/components/shared/model-card";
import { AnimatedSection } from "@/components/shared/animated-section";
import {
    deleteModel,
    getToken,
    listModels,
    type BackendCustomModel,
} from "@/lib/api";
import { backendModelToUiModel } from "@/lib/model-adapter";
import type { CustomModel } from "@/lib/types";

export default function DashboardPage() {
    const router = useRouter();

    const [backendModels, setBackendModels] = useState<BackendCustomModel[]>([]);
    const [models, setModels] = useState<CustomModel[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [deletingModelId, setDeletingModelId] = useState<string | null>(null);

    useEffect(() => {
        async function loadDashboard() {
            if (!getToken()) {
                router.replace("/login");
                return;
            }

            try {
                setLoading(true);
                setError("");

                const data = await listModels();
                setBackendModels(data);
                setModels(data.map(backendModelToUiModel));
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load dashboard");
            } finally {
                setLoading(false);
            }
        }

        loadDashboard();
    }, [router]);

    async function handleDeleteModel(model: CustomModel) {
        const confirmed = window.confirm(
            `Delete "${model.name}"? This cannot be undone.`
        );

        if (!confirmed) return;

        try {
            setError("");
            setDeletingModelId(model.id);

            await deleteModel(model.id);

            setBackendModels((current) =>
                current.filter((item) => item.id !== model.id)
            );

            setModels((current) =>
                current.filter((item) => item.id !== model.id)
            );
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to delete model");
        } finally {
            setDeletingModelId(null);
        }
    }

    const averageReadiness = useMemo(() => {
        if (backendModels.length === 0) return 0;

        const total = backendModels.reduce(
            (sum, model) => sum + (model.readiness_score ?? 0),
            0
        );

        return Math.round(total / backendModels.length);
    }, [backendModels]);

    const trainedCount = backendModels.filter((model) =>
        ["trained", "deployed"].includes(model.status)
    ).length;

    const trainingCount = backendModels.filter(
        (model) => model.status === "training"
    ).length;

    return (
        <div className="space-y-8">
            <PageHeader
                eyebrow="Dashboard"
                title="Build, train, deploy, and improve your models."
                description="Track model readiness, training progress, API usage, and reviewed feedback from one workspace."
                actions={
                    <Button asChild>
                        <Link href="/models/new">
                            <Plus className="h-4 w-4" /> Create model
                        </Link>
                    </Button>
                }
            />

            {error ? (
                <div className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                    {error}
                </div>
            ) : null}

            <div className="grid gap-4 md:grid-cols-3">
                <MetricCard
                    label="Models"
                    value={String(backendModels.length)}
                    helper="Real backend models"
                    icon={Bot}
                    delay={0}
                />
                <MetricCard
                    label="Avg readiness"
                    value={`${averageReadiness}%`}
                    helper="From backend readiness score"
                    icon={TrendingUp}
                    delay={0.05}
                />
                <MetricCard
                    label="Trained models"
                    value={String(trainedCount)}
                    helper={`${trainingCount} currently training`}
                    icon={Rocket}
                    delay={0.1}
                />
            </div>

            <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
                <section>
                    <div className="mb-4 flex items-center justify-between">
                        <h2 className="text-xl font-semibold">Your models</h2>
                        <Button variant="ghost" asChild>
                            <Link href="/models/new">
                                New model <ArrowRight className="h-4 w-4" />
                            </Link>
                        </Button>
                    </div>

                    {loading ? (
                        <Card>
                            <CardContent className="p-8 text-sm text-muted-foreground">
                                Loading your models...
                            </CardContent>
                        </Card>
                    ) : models.length > 0 ? (
                        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                            {models.map((model) => {
                                const deleting = deletingModelId === model.id;

                                return (
                                    <div key={model.id} className="space-y-3">
                                        <ModelCard model={model} />

                                        <Button
                                            type="button"
                                            variant="outline"
                                            className="w-full justify-between border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700"
                                            onClick={() => handleDeleteModel(model)}
                                            disabled={deleting}
                                        >
                                            {deleting ? "Deleting..." : "Delete model"}
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <Card>
                            <CardContent className="p-8">
                                <div className="mx-auto max-w-md text-center">
                                    <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-muted">
                                        <Bot className="h-6 w-6 text-primary" />
                                    </div>
                                    <h3 className="text-lg font-semibold">No models yet</h3>
                                    <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                        Create your first model, upload training data, validate readiness,
                                        and start the model training workflow.
                                    </p>
                                    <Button asChild className="mt-5">
                                        <Link href="/models/new">
                                            <Plus className="h-4 w-4" /> Create model
                                        </Link>
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </section>

                <aside className="space-y-6">
                    <AnimatedSection delay={0.1}>
                        <Card className="bg-slate-950 text-white">
                            <CardContent className="p-6">
                                <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10">
                                    <Rocket className="h-5 w-5 text-cyan-300" />
                                </div>
                                <h3 className="text-lg font-semibold">Next step</h3>
                                <p className="mt-2 text-sm leading-6 text-slate-300">
                                    Create a model, upload data, validate readiness, train, version,
                                    test, and deploy it through an API key.
                                </p>
                                <Button asChild variant="secondary" className="mt-5 w-full">
                                    <Link href="/models/new">Create model</Link>
                                </Button>
                            </CardContent>
                        </Card>
                    </AnimatedSection>

                    <Card>
                        <CardHeader>
                            <CardTitle>Backend status</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {[
                                {
                                    icon: CheckCircle2,
                                    label: "Auth connected",
                                    detail: "Signup/login uses FastAPI.",
                                },
                                {
                                    icon: Database,
                                    label: "Models connected",
                                    detail: "Dashboard reads PostgreSQL through backend.",
                                },
                                {
                                    icon: Rocket,
                                    label: "Training backend ready",
                                    detail: "Jobs, versions, API keys, and inference are connected.",
                                },
                            ].map((item) => {
                                const Icon = item.icon;

                                return (
                                    <div key={item.label} className="flex gap-3">
                                        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-muted">
                                            <Icon className="h-4 w-4 text-primary" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-semibold">{item.label}</p>
                                            <p className="text-xs text-muted-foreground">
                                                {item.detail}
                                            </p>
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