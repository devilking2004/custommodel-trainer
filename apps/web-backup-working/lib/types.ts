export type ModelCategory = "text_to_text" | "text_to_image";
export type ModelVisibility = "private" | "unlisted" | "public";
export type ModelStatus = "draft" | "dataset_ready" | "training" | "deployed" | "archived";

export type User = {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: User;
};

export type CustomModel = {
  id: string;
  owner_id: string;
  name: string;
  description: string | null;
  category: ModelCategory;
  visibility: ModelVisibility;
  status: ModelStatus;
  icon_url: string | null;
  improve_from_feedback: boolean;
  created_at: string;
  updated_at: string;
};

export type CustomModelCreate = {
  name: string;
  description?: string | null;
  category: ModelCategory;
  visibility: ModelVisibility;
  icon_url?: string | null;
  improve_from_feedback: boolean;
};
