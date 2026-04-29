import { Badge } from "@/components/ui/badge";
import type { ModelStatus } from "@/lib/types";

export function StatusBadge({ status }: { status: ModelStatus | "Passed" | "Warning" | "Failed" | "Active" | "Archived" }) {
  if (status === "Ready" || status === "Passed" || status === "Active" || status === "Deployed") {
    return <Badge variant="success">{status}</Badge>;
  }

  if (status === "Training" || status === "Warning") {
    return <Badge variant="warning">{status}</Badge>;
  }

  if (status === "Failed") {
    return <Badge variant="danger">{status}</Badge>;
  }

  return <Badge variant="muted">{status}</Badge>;
}
