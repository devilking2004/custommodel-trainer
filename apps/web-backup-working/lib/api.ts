import type { AuthResponse, CustomModel, CustomModelCreate, User } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const TOKEN_KEY = "custommodel_trainer_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

type ApiErrorBody = {
  detail?: string | { msg?: string }[];
};

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const hasBody = typeof options.body !== "undefined";

  if (hasBody && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as ApiErrorBody;
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail) && body.detail.length > 0) {
        message = body.detail.map((item) => item.msg ?? "Validation error").join(", ");
      }
    } catch {
      // Keep the default error message when the server does not return JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function signup(payload: { email: string; password: string; full_name?: string }) {
  return apiFetch<AuthResponse>("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function login(payload: { email: string; password: string }) {
  return apiFetch<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMe() {
  return apiFetch<User>("/users/me");
}

export async function listModels() {
  const response = await apiFetch<{ items: CustomModel[] }>("/models");
  return response.items;
}

export function createModel(payload: CustomModelCreate) {
  return apiFetch<CustomModel>("/models", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
