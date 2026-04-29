export type ModelCategory = "Text-to-Text" | "Text-to-Image";
export type ModelStatus = "Draft" | "Ready" | "Training" | "Deployed";
export type Visibility = "Private" | "Workspace" | "Public";

export type CustomModel = {
  id: string;
  name: string;
  description: string;
  category: ModelCategory;
  status: ModelStatus;
  readinessScore: number;
  version: string;
  icon: string;
  visibility: Visibility;
  feedbackEnabled: boolean;
  requests: number;
  latencyMs: number;
  updatedAt: string;
};

export type ReadinessCheck = {
  label: string;
  description: string;
  status: "Passed" | "Warning" | "Failed";
  score: number;
};

export type TrainingStep = {
  label: string;
  status: "Complete" | "Current" | "Pending";
  detail: string;
};

export type FeedbackItem = {
  id: string;
  prompt: string;
  output: string;
  rating: "Positive" | "Negative" | "Neutral";
  note: string;
  source: "Playground" | "API";
  reviewed: boolean;
  createdAt: string;
};

export type VersionItem = {
  id: string;
  version: string;
  status: "Active" | "Archived";
  score: number;
  createdAt: string;
  notes: string;
  trainingRows: number;
};
