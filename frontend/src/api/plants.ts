import type {
  CareLogEntry,
  IdentifyResponse,
  Plant,
  PlantCreate,
  PlantUpdate,
  ScheduledPlant,
  WaterResponse,
} from "../types/plant";

const BASE = "/plants";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

function json<T>(url: string, method: string, body: unknown): Promise<T> {
  return request<T>(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  list: () => request<Plant[]>(BASE),
  get: (id: string) => request<Plant>(`${BASE}/${id}`),
  create: (data: PlantCreate) => json<Plant>(BASE, "POST", data),
  update: (id: string, data: PlantUpdate) => json<Plant>(`${BASE}/${id}`, "PUT", data),
  delete: (id: string) => request<void>(`${BASE}/${id}`, { method: "DELETE" }),

  identifyImage: (id: string, file: File, organ = "auto"): Promise<IdentifyResponse> => {
    const form = new FormData();
    form.append("image", file);
    form.append("organ", organ);
    return request<IdentifyResponse>(`${BASE}/${id}/identify`, { method: "POST", body: form });
  },

  water: (id: string) =>
    request<WaterResponse>(`${BASE}/${id}/water`, { method: "POST" }),

  logCare: (id: string, action: string, notes?: string) =>
    json<CareLogEntry>(`${BASE}/${id}/care-log`, "POST", { action, notes }),

  getCareLog: (id: string) => request<CareLogEntry[]>(`${BASE}/${id}/care-log`),

  getSchedule: (dueToday = false) =>
    request<ScheduledPlant[]>(`/schedule${dueToday ? "?due_today=true" : ""}`),
};
