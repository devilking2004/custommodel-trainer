import type { CustomModel, FeedbackItem, ReadinessCheck, TrainingStep, VersionItem } from "@/lib/types";

export const demoModelId = "demo-cx-bot";

export const models: CustomModel[] = [
  {
    id: demoModelId,
    name: "CX Answer Bot",
    description: "A support assistant fine-tuned on customer questions, refund rules, and onboarding docs.",
    category: "Text-to-Text",
    status: "Training",
    readinessScore: 86,
    version: "v1.3",
    icon: "💬",
    visibility: "Private",
    feedbackEnabled: true,
    requests: 18420,
    latencyMs: 412,
    updatedAt: "2026-04-24"
  },
  {
    id: "brand-style-image-lora",
    name: "Brand Style Image LoRA",
    description: "Generates product visuals in a soft studio lighting style using uploaded brand examples.",
    category: "Text-to-Image",
    status: "Deployed",
    readinessScore: 92,
    version: "v2.1",
    icon: "🎨",
    visibility: "Workspace",
    feedbackEnabled: true,
    requests: 9340,
    latencyMs: 1830,
    updatedAt: "2026-04-21"
  },
  {
    id: "summary-helper",
    name: "Article Summary Helper",
    description: "Turns long internal research notes into concise summaries for product teams.",
    category: "Text-to-Text",
    status: "Ready",
    readinessScore: 78,
    version: "v1.0",
    icon: "📝",
    visibility: "Private",
    feedbackEnabled: false,
    requests: 2140,
    latencyMs: 355,
    updatedAt: "2026-04-20"
  }
];

export const readinessChecks: ReadinessCheck[] = [
  {
    label: "Required fields",
    description: "All rows include input and output values.",
    status: "Passed",
    score: 100
  },
  {
    label: "Duplicate examples",
    description: "48 near-duplicates found. Review before training for better generalization.",
    status: "Warning",
    score: 76
  },
  {
    label: "Output quality",
    description: "Most answers are specific, complete, and written in a consistent support tone.",
    status: "Passed",
    score: 91
  },
  {
    label: "Length balance",
    description: "Some outputs are much shorter than expected for complex questions.",
    status: "Warning",
    score: 72
  },
  {
    label: "Safety review",
    description: "No sensitive tokens, private keys, or obvious personal data found in sample scan.",
    status: "Passed",
    score: 94
  }
];

export const trainingSteps: TrainingStep[] = [
  {
    label: "Dataset prepared",
    status: "Complete",
    detail: "12,420 examples cleaned and split into train/eval sets."
  },
  {
    label: "Adapter initialized",
    status: "Complete",
    detail: "LoRA adapter created with safe default rank and learning rate."
  },
  {
    label: "Fine-tuning",
    status: "Current",
    detail: "Epoch 2 of 3 is running. Current eval loss is improving."
  },
  {
    label: "Evaluation",
    status: "Pending",
    detail: "The model will be tested against holdout examples."
  },
  {
    label: "Version created",
    status: "Pending",
    detail: "A new version will be available for playground testing."
  }
];

export const trainingLogs = [
  "Queued job train_8d9f2 for CX Answer Bot",
  "Loaded cleaned dataset: 12,420 rows",
  "Validation split created: 1,242 rows",
  "LoRA adapter initialized",
  "Epoch 1/3 complete — eval_loss=0.824",
  "Epoch 2/3 running — step 640/930",
  "GPU utilization stable at 78%",
  "Estimated quality score improving"
];

export const feedbackItems: FeedbackItem[] = [
  {
    id: "fb_001",
    prompt: "How do I upgrade from Starter to Pro?",
    output: "Open billing settings, choose Pro, and confirm the payment method.",
    rating: "Positive",
    note: "Good answer. Could mention that changes apply immediately.",
    source: "Playground",
    reviewed: false,
    createdAt: "2026-04-25"
  },
  {
    id: "fb_002",
    prompt: "Can I get a refund after 45 days?",
    output: "Yes, refunds are available within 60 days.",
    rating: "Negative",
    note: "Wrong. Our policy is 30 days except enterprise contracts.",
    source: "API",
    reviewed: false,
    createdAt: "2026-04-25"
  },
  {
    id: "fb_003",
    prompt: "Where can I find invoices?",
    output: "Invoices are available in workspace billing under Payment history.",
    rating: "Positive",
    note: "Useful and concise.",
    source: "API",
    reviewed: true,
    createdAt: "2026-04-23"
  }
];

export const versions: VersionItem[] = [
  {
    id: "ver_003",
    version: "v1.3",
    status: "Active",
    score: 89,
    createdAt: "2026-04-24",
    notes: "Added approved feedback from API usage and improved refund-policy examples.",
    trainingRows: 12420
  },
  {
    id: "ver_002",
    version: "v1.2",
    status: "Archived",
    score: 84,
    createdAt: "2026-04-18",
    notes: "Improved onboarding answers and removed duplicate examples.",
    trainingRows: 10280
  },
  {
    id: "ver_001",
    version: "v1.0",
    status: "Archived",
    score: 76,
    createdAt: "2026-04-12",
    notes: "First fine-tuned version from uploaded support FAQ dataset.",
    trainingRows: 8240
  }
];

export const usageSeries = [
  { label: "Mon", value: 2100 },
  { label: "Tue", value: 3200 },
  { label: "Wed", value: 2800 },
  { label: "Thu", value: 4100 },
  { label: "Fri", value: 3900 },
  { label: "Sat", value: 1800 },
  { label: "Sun", value: 2340 }
];

export const samplePrompts = [
  "How do I reset my password?",
  "Summarize our refund policy in one paragraph.",
  "Write a friendly answer for a user whose payment failed.",
  "What should I do if my invite link expired?"
];
