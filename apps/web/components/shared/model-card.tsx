import Link from "next/link";
import { ArrowRight, Clock3, Gauge, Zap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/shared/status-badge";
import type { CustomModel } from "@/lib/types";
import { formatNumber } from "@/lib/utils";

export function ModelCard({ model }: { model: CustomModel }) {
  return (
    <Card className="group h-full overflow-hidden transition-all hover:-translate-y-1 hover:shadow-xl hover:shadow-slate-200/70">
      <CardContent className="flex h-full flex-col p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted text-2xl">{model.icon}</div>
            <div>
              <h3 className="font-semibold">{model.name}</h3>
              <p className="text-xs text-muted-foreground">{model.category} · {model.version}</p>
            </div>
          </div>
          <StatusBadge status={model.status} />
        </div>
        <p className="mt-4 line-clamp-2 text-sm leading-6 text-muted-foreground">{model.description}</p>

        <div className="mt-5 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="flex items-center gap-1 text-muted-foreground"><Gauge className="h-3.5 w-3.5" /> Readiness</span>
            <span className="font-semibold">{model.readinessScore}%</span>
          </div>
          <Progress value={model.readinessScore} />
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3 text-xs">
          <div className="rounded-xl bg-muted p-3">
            <p className="flex items-center gap-1 text-muted-foreground"><Zap className="h-3.5 w-3.5" /> Requests</p>
            <p className="mt-1 font-semibold">{formatNumber(model.requests)}</p>
          </div>
          <div className="rounded-xl bg-muted p-3">
            <p className="flex items-center gap-1 text-muted-foreground"><Clock3 className="h-3.5 w-3.5" /> Latency</p>
            <p className="mt-1 font-semibold">{model.latencyMs}ms</p>
          </div>
        </div>

        <Button asChild variant="outline" className="mt-5 w-full justify-between">
          <Link href={`/models/${model.id}/setup`}>
            Open model
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
