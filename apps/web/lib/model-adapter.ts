import type { CustomModel } from "@/lib/types";
import type { BackendCustomModel } from "@/lib/api";

export function backendModelToUiModel(model: BackendCustomModel): CustomModel {
  return {
    id: model.id,
    name: model.name,
    description: model.description ?? "No description yet.",
    category: model.category === "text_to_text" ? "Text-to-Text" : "Text-to-Image",
    status: mapStatus(model.status),
    readinessScore: model.readiness_score ?? 0,
    version: model.current_version_id ? "v1" : "v0",
    icon: model.category === "text_to_text" ? "💬" : "🎨",
    visibility: model.visibility === "private" ? "Private" : "Public",
    feedbackEnabled: model.improve_from_feedback,
    requests: 0,
    latencyMs: 0,
    updatedAt: model.updated_at.slice(0, 10),
  };
}

function mapStatus(status: BackendCustomModel["status"]): CustomModel["status"] {
  if (status === "training") return "Training";
  if (status === "trained" || status === "deployed") return "Deployed";
  if (status === "data_ready") return "Ready";
  return "Draft";
}