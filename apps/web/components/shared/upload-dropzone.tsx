"use client";

import { useRef, useState } from "react";
import { FileText, ImageIcon, UploadCloud, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function UploadDropzone({ type }: { type: "text" | "image" }) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [files, setFiles] = useState<string[]>(["customer-support-samples.csv", "refund-policy-examples.jsonl"]);

  function addMockFile() {
    const mockFile = type === "text" ? "new-training-examples.csv" : "brand-image-manifest.jsonl";
    setFiles((current) => Array.from(new Set([...current, mockFile])));
  }

  return (
    <div>
      <button
        type="button"
        onClick={() => {
          inputRef.current?.click();
          addMockFile();
        }}
        className={cn(
          "group flex min-h-64 w-full flex-col items-center justify-center rounded-3xl border border-dashed bg-card p-8 text-center transition-all hover:-translate-y-1 hover:border-primary hover:shadow-xl hover:shadow-slate-200/60"
        )}
      >
        <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-3xl bg-secondary text-secondary-foreground transition-transform group-hover:scale-105">
          <UploadCloud className="h-8 w-8" />
        </div>
        <h3 className="text-lg font-semibold">Drop your dataset here</h3>
        <p className="mt-2 max-w-md text-sm leading-6 text-muted-foreground">
          {type === "text"
            ? "Upload CSV or JSONL files with input and output columns."
            : "Upload image folders plus a JSONL manifest with image_path and caption."}
        </p>
        <span className="mt-5 rounded-full bg-muted px-4 py-2 text-sm font-medium text-muted-foreground">Choose files</span>
      </button>
      <input ref={inputRef} type="file" multiple className="hidden" />

      <div className="mt-5 space-y-3">
        {files.map((file) => (
          <div key={file} className="flex items-center justify-between rounded-2xl border bg-card p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-muted">
                {type === "text" ? <FileText className="h-5 w-5 text-primary" /> : <ImageIcon className="h-5 w-5 text-primary" />}
              </div>
              <div>
                <p className="text-sm font-semibold">{file}</p>
                <p className="text-xs text-muted-foreground">Mock uploaded · ready for validation</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setFiles((current) => current.filter((item) => item !== file))} aria-label={`Remove ${file}`}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
