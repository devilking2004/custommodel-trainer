import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import type { TrainingStep } from "@/lib/types";
import { cn } from "@/lib/utils";

export function ProgressStepper({ steps }: { steps: TrainingStep[] }) {
  return (
    <div className="space-y-4">
      {steps.map((step, index) => {
        const isComplete = step.status === "Complete";
        const isCurrent = step.status === "Current";

        return (
          <div key={step.label} className="relative flex gap-4">
            {index !== steps.length - 1 ? <div className="absolute left-5 top-10 h-full w-px bg-border" /> : null}
            <div
              className={cn(
                "z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border bg-card",
                isComplete && "border-emerald-200 bg-emerald-50 text-emerald-600",
                isCurrent && "border-amber-200 bg-amber-50 text-amber-600"
              )}
            >
              {isComplete ? <CheckCircle2 className="h-5 w-5" /> : isCurrent ? <Loader2 className="h-5 w-5 animate-spin" /> : <Circle className="h-5 w-5" />}
            </div>
            <div className="pb-6">
              <p className="font-semibold">{step.label}</p>
              <p className="mt-1 text-sm leading-6 text-muted-foreground">{step.detail}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
