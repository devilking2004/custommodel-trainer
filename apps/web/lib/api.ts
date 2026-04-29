const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const TOKEN_KEY = "custommodel_trainer_access_token";

export type BackendUser = {
    id: string;
    email: string;
    full_name: string | null;
    is_active: boolean;
    created_at: string;
};

export type AuthResponse = {
    access_token: string;
    token_type: string;
    user: BackendUser;
};

export type BackendModelCategory = "text_to_text" | "text_to_image";

export type BackendModelVisibility = "private" | "public" | "unlisted";

export type BackendModelStatus =
    | "draft"
    | "data_ready"
    | "training"
    | "trained"
    | "deployed"
    | "archived";

export type BackendCustomModel = {
    id: string;
    owner_id: string;
    name: string;
    slug: string;
    description: string | null;
    category: BackendModelCategory;
    visibility: BackendModelVisibility;
    status: BackendModelStatus;
    icon_url: string | null;
    improve_from_feedback: boolean;
    readiness_score: number;
    current_version_id: string | null;
    created_at: string;
    updated_at: string;
};

export type CustomModelCreate = {
    name: string;
    description?: string | null;
    category: BackendModelCategory;
    visibility: BackendModelVisibility;
    improve_from_feedback: boolean;
};

export type CustomModelUpdate = Partial<{
    name: string;
    description: string | null;
    visibility: BackendModelVisibility;
    improve_from_feedback: boolean;
}>;

export type BackendDataset = {
    id: string;
    owner_id: string;
    model_id: string;
    name: string;
    status: string;
    readiness_score: number;
    row_count: number;
    valid_count: number;
    invalid_count: number;
    issue_summary: Record<string, unknown>;
    dataset_metadata: Record<string, unknown>;
    created_at: string;
    updated_at: string;
};

export type BackendStoredFile = {
    id: string;
    model_id: string | null;
    dataset_id: string | null;
    kind: string;
    original_filename: string;
    content_type: string | null;
    size_bytes: number;
    checksum_sha256: string;
    storage_bucket: string;
    storage_key: string;
    public_url: string | null;
    created_at: string;
};

export type BackendDataIssue = {
    id: string;
    severity: "info" | "warning" | "error";
    code: string;
    message: string;
    row_number: number | null;
    field: string | null;
    details: Record<string, unknown>;
    created_at: string;
};

export type DatasetValidationResponse = {
    dataset: BackendDataset;
    issues: BackendDataIssue[];
};

export type BackendTrainingJob = {
    id: string;
    owner_id: string;
    model_id: string;
    dataset_id: string | null;
    job_type: "initial" | "retrain";
    status: "queued" | "running" | "succeeded" | "failed" | "cancelled";
    progress: number;
    current_step: string | null;
    rq_job_id: string | null;
    logs: unknown[];
    error_message: string | null;
    training_config: Record<string, unknown>;
    started_at: string | null;
    completed_at: string | null;
    created_at: string;
    updated_at: string;
};

export type BackendModelVersion = {
    id: string;
    owner_id: string;
    model_id: string;
    training_job_id: string | null;
    version_number: number;
    name: string;
    status: "active" | "archived" | "failed";
    is_active: boolean;
    base_model: string | null;
    artifact_file_id: string | null;
    artifact_storage_key: string | null;
    metrics: Record<string, unknown>;
    notes: string | null;
    created_at: string;
    updated_at: string;
};

export type BackendApiKey = {
    id: string;
    model_id: string;
    name: string;
    key_prefix: string;
    status: string;
    last_used_at: string | null;
    expires_at: string | null;
    revoked_at: string | null;
    created_at: string;
};

export type BackendApiKeyCreated = {
    api_key: string;
    record: BackendApiKey;
};

export type BackendInferenceResponse = {
    request_id: string;
    model_id: string;
    model_version_id: string | null;
    output: string | Record<string, unknown>;
    latency_ms: number;
    usage: Record<string, unknown>;
};

export type BackendFeedback = {
    id: string;
    owner_id: string;
    model_id: string;
    model_version_id: string | null;
    inference_request_id: string | null;
    input: string | null;
    output: string | Record<string, unknown> | null;
    rating: number | null;
    comment: string | null;
    correction: string | null;
    status: "pending" | "approved" | "rejected";
    approved_for_training: boolean;
    reviewed_at: string | null;
    created_at: string;
    updated_at: string;
};

export type BackendUsageLog = {
    id: string;
    owner_id: string;
    model_id: string;
    model_version_id: string | null;
    api_key_id: string | null;
    request_id: string;
    endpoint: string;
    status_code: number;
    latency_ms: number;
    input_units: number;
    output_units: number;
    error_message: string | null;
    created_at: string;
};

export function getToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(TOKEN_KEY);
}

type ApiErrorBody = {
    detail?: string | Array<{ msg?: string }> | Record<string, unknown>;
};

function getErrorMessage(body: ApiErrorBody, fallback: string): string {
    if (typeof body.detail === "string") {
        return body.detail;
    }

    if (Array.isArray(body.detail)) {
        return body.detail
            .map((item) => item.msg ?? "Validation error")
            .join(", ");
    }

    return fallback;
}

async function parseResponse<T>(response: Response): Promise<T> {
    if (response.status === 204) {
        return undefined as T;
    }

    const text = await response.text();

    if (!text) {
        return undefined as T;
    }

    return JSON.parse(text) as T;
}

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers);

    if (
        options.body &&
        !(options.body instanceof FormData) &&
        !headers.has("Content-Type")
    ) {
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
        const fallback = `Request failed with status ${response.status}`;
        let message = fallback;

        try {
            const body = (await response.json()) as ApiErrorBody;
            message = getErrorMessage(body, fallback);
        } catch {
            // Keep fallback message.
        }

        throw new Error(message);
    }

    return parseResponse<T>(response);
}

/* Auth */

export function signup(payload: {
    email: string;
    password: string;
    full_name?: string;
}) {
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
    return apiFetch<BackendUser>("/users/me");
}

/* Models */

export function listModels() {
    return apiFetch<BackendCustomModel[]>("/models");
}

export function createModel(payload: CustomModelCreate) {
    return apiFetch<BackendCustomModel>("/models", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function getModel(modelId: string) {
    return apiFetch<BackendCustomModel>(`/models/${modelId}`);
}

export function updateModel(modelId: string, payload: CustomModelUpdate) {
    return apiFetch<BackendCustomModel>(`/models/${modelId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
    });
}

export function deleteModel(modelId: string) {
    return apiFetch<void>(`/models/${modelId}`, {
        method: "DELETE",
    });
}

/* Datasets */

export function createDataset(modelId: string, payload: { name: string }) {
    return apiFetch<BackendDataset>(`/models/${modelId}/datasets`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function listDatasets(modelId: string) {
    return apiFetch<BackendDataset[]>(`/models/${modelId}/datasets`);
}

export function getDataset(datasetId: string) {
    return apiFetch<BackendDataset>(`/datasets/${datasetId}`);
}

export function uploadDatasetFile(datasetId: string, file: File) {
    const formData = new FormData();
    formData.append("upload", file);

    return apiFetch<BackendStoredFile>(`/datasets/${datasetId}/files`, {
        method: "POST",
        body: formData,
    });
}

export function validateDataset(datasetId: string) {
    return apiFetch<DatasetValidationResponse>(`/datasets/${datasetId}/validate`, {
        method: "POST",
    });
}

export function getDatasetReadiness(datasetId: string) {
    return apiFetch<DatasetValidationResponse>(`/datasets/${datasetId}/readiness`);
}

/* Training */

export function startTraining(
    modelId: string,
    payload: {
        dataset_id?: string | null;
        base_model?: string | null;
        epochs?: number;
        learning_rate?: number;
        notes?: string | null;
    }
) {
    return apiFetch<BackendTrainingJob>(`/models/${modelId}/train`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function requestRetraining(
    modelId: string,
    payload: {
        dataset_id?: string | null;
        base_model?: string | null;
        epochs?: number;
        learning_rate?: number;
        notes?: string | null;
    }
) {
    return apiFetch<BackendTrainingJob>(`/models/${modelId}/retrain`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function getTrainingJob(jobId: string) {
    return apiFetch<BackendTrainingJob>(`/training-jobs/${jobId}`);
}

/* Versions */

export function listVersions(modelId: string) {
    return apiFetch<BackendModelVersion[]>(`/models/${modelId}/versions`);
}

export function rollbackVersion(modelId: string, versionId: string) {
    return apiFetch<BackendModelVersion>(
        `/models/${modelId}/versions/${versionId}/rollback`,
        {
            method: "POST",
        }
    );
}

/* API keys */

export function createApiKey(modelId: string, payload: { name: string }) {
    return apiFetch<BackendApiKeyCreated>(`/models/${modelId}/api-keys`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function listApiKeys(modelId: string) {
    return apiFetch<BackendApiKey[]>(`/models/${modelId}/api-keys`);
}

export function deleteApiKey(apiKeyId: string) {
    return apiFetch<void>(`/api-keys/${apiKeyId}`, {
        method: "DELETE",
    });
}

/* Inference */

export async function runInference(
    modelId: string,
    apiKey: string,
    payload: {
        input: string;
        parameters?: Record<string, unknown>;
    }
) {
    const response = await fetch(`${API_BASE_URL}/api/v1/inference/${modelId}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-API-Key": apiKey,
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const fallback = `Inference failed with status ${response.status}`;
        let message = fallback;

        try {
            const body = (await response.json()) as ApiErrorBody;
            message = getErrorMessage(body, fallback);
        } catch {
            // Keep fallback message.
        }

        throw new Error(message);
    }

    return parseResponse<BackendInferenceResponse>(response);
}

/* Feedback */

export function listFeedback(modelId: string) {
    return apiFetch<BackendFeedback[]>(`/models/${modelId}/feedback`);
}

export function createFeedback(
    modelId: string,
    payload: {
        input?: string | null;
        output?: string | Record<string, unknown> | null;
        rating?: number | null;
        comment?: string | null;
        correction?: string | null;
        inference_request_id?: string | null;
        model_version_id?: string | null;
    }
) {
    return apiFetch<BackendFeedback>(`/models/${modelId}/feedback`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function createInferenceFeedback(
    modelId: string,
    payload: {
        inference_request_id: string;
        rating?: number | null;
        comment?: string | null;
        correction?: string | null;
    }
) {
    return apiFetch<BackendFeedback>(`/inference/${modelId}/feedback`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function reviewFeedback(
    feedbackId: string,
    payload: {
        status: "approved" | "rejected";
        approved_for_training?: boolean;
    }
) {
    return apiFetch<BackendFeedback>(`/feedback/${feedbackId}/review`, {
        method: "PATCH",
        body: JSON.stringify(payload),
    });
}

/* Usage */

export function listUsage(modelId: string) {
    return apiFetch<BackendUsageLog[]>(`/models/${modelId}/usage`);
}