import { Bot, ImageIcon, Lock, MessageSquare, ShieldCheck } from "lucide-react";

import type { CustomModel } from "@/lib/types";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";

export function ModelCard({ model }: { model: CustomModel }) {
  const isTextToText = model.category === "text_to_text";
  const Icon = isTextToText ? MessageSquare : ImageIcon;

  return (
    <Card className="transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-100 text-slate-800">
            {model.icon_url ? <Bot className="h-5 w-5" /> : <Icon className="h-5 w-5" />}
          </div>
          <div>
            <CardTitle>{model.name}</CardTitle>
            <CardDescription>{isTextToText ? "Text-to-Text" : "Text-to-Image"}</CardDescription>
          </div>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold capitalize text-slate-700">
          {model.status.replaceAll("_", " ")}
        </span>
      </div>

      <p className="mt-5 line-clamp-2 text-sm leading-6 text-slate-600">
        {model.description || "No description yet."}
      </p>

      <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium text-slate-600">
        <span className="inline-flex items-center rounded-full bg-slate-50 px-3 py-1">
          <Lock className="mr-1 h-3.5 w-3.5" /> {model.visibility}
        </span>
        {model.improve_from_feedback && (
          <span className="inline-flex items-center rounded-full bg-slate-50 px-3 py-1">
            <ShieldCheck className="mr-1 h-3.5 w-3.5" /> feedback review enabled
          </span>
        )}
      </div>
    </Card>
  );
}
