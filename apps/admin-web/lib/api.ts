import { API_BASE_URL } from "@/lib/config";
import type {
  AdminOut,
  ApplicationDetail,
  ApplicationListResponse,
  ApplicationPriority,
  ApplicationStatus,
  ApplicationType,
  DashboardStats,
  ReportStats,
  SystemSettingsOut,
} from "@/lib/types";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

const MUTATING = new Set(["POST", "PATCH", "PUT", "DELETE"]);

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method || "GET").toUpperCase();
  const headers: Record<string, string> = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(options.headers as Record<string, string>),
  };
  if (MUTATING.has(method)) {
    const csrf = getCookie("csrf_token");
    if (csrf) headers["X-CSRF-Token"] = csrf;
  }

  const resp = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    method,
    headers,
    credentials: "include",
  });

  if (resp.status === 204) return undefined as T;

  const isJson = resp.headers.get("content-type")?.includes("application/json");
  const body = isJson ? await resp.json() : await resp.text();

  if (!resp.ok) {
    const message = isJson && body?.detail ? body.detail : "Сервер қатесі";
    throw new ApiError(message, resp.status);
  }
  return body as T;
}

// ---- Auth ----
export const authApi = {
  login: (email: string, password: string) =>
    request<{ admin: AdminOut; csrf_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => request<{ detail: string }>("/auth/logout", { method: "POST" }),
  me: () => request<AdminOut>("/auth/me"),
};

// ---- Applications ----
export interface ApplicationFilters {
  application_number?: string;
  personal_account?: string;
  application_type?: ApplicationType;
  status?: ApplicationStatus;
  priority?: ApplicationPriority;
  date_from?: string;
  date_to?: string;
  q?: string;
  sort?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

function toQuery(filters: object): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") params.set(key, String(value));
  });
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const applicationsApi = {
  list: (filters: ApplicationFilters) =>
    request<ApplicationListResponse>(`/applications${toQuery(filters)}`),
  get: (id: number) => request<ApplicationDetail>(`/applications/${id}`),
  updateStatus: (id: number, status: ApplicationStatus, comment?: string) =>
    request<ApplicationDetail>(`/applications/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, comment }),
    }),
  assign: (id: number, assigned_to: number | null) =>
    request<ApplicationDetail>(`/applications/${id}/assign`, {
      method: "PATCH",
      body: JSON.stringify({ assigned_to }),
    }),
  addComment: (id: number, comment: string) =>
    request<ApplicationDetail>(`/applications/${id}/comments`, {
      method: "POST",
      body: JSON.stringify({ comment }),
    }),
  history: (id: number) => request(`/applications/${id}/history`),
  exportUrl: (filters: ApplicationFilters, format: "csv" | "xlsx") =>
    `${API_BASE_URL}/applications/export${toQuery({ ...filters, format })}`,
};

// ---- Dashboard ----
export interface ReportFilters {
  application_type?: ApplicationType;
  status?: ApplicationStatus;
  assigned_to?: number;
  date_from?: string;
  date_to?: string;
}

export const dashboardApi = {
  stats: () => request<DashboardStats>("/dashboard/stats"),
  report: (filters: ReportFilters) => request<ReportStats>(`/dashboard/report${toQuery(filters)}`),
};

// ---- Admins ----
export const adminsApi = {
  list: () => request<AdminOut[]>("/admins"),
  create: (data: { name: string; email: string; password: string; role: string }) =>
    request<AdminOut>("/admins", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<{ name: string; role: string; active: boolean; password: string }>) =>
    request<AdminOut>(`/admins/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
};

// ---- Settings ----
export const settingsApi = {
  get: () => request<SystemSettingsOut>("/settings"),
  update: (data: Partial<SystemSettingsOut>) =>
    request<SystemSettingsOut>("/settings", { method: "PATCH", body: JSON.stringify(data) }),
};

// ---- Application types ----
export const applicationTypesApi = {
  list: () => request<{ value: ApplicationType; label_kk: string }[]>("/application-types"),
};
