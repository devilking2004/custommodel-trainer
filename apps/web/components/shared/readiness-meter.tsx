import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export function ReadinessMeter({ score }: { score: number }) {
  const label = score >= 85 ? "Ready to train" : score >= 70 ? "Almost ready" : "Needs cleanup";

  return (
    <Card className="overflow-hidden bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <CardContent className="p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Data Readiness Score</p>
            <div className="mt-2 flex items-end gap-2">
              <span className="text-6xl font-bold tracking-tight">{score}</span>
              <span className="mb-2 text-lg font-semibold text-muted-foreground">/ 100</span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{label}. Review warnings before training for better results.</p>
          </div>
          <div className="flex h-32 w-32 items-center justify-center rounded-full border-[10px] border-indigo-100 bg-white shadow-inner">
            <span className="text-3xl font-bold text-primary">{score}%</span>
          </div>
        </div>
        <div className="mt-6">
          <Progress value={score} className="h-4" />
        </div>
      </CardContent>
    </Card>
  );
}
