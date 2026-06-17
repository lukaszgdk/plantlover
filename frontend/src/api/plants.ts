import type {
  CareLogEntry,
  IdentifyNewResponse,
  IdentifyResponse,
  Plant,
  PlantUpdate,
  Room,
  ScheduledPlant,
  SunlightLevel,
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
  // ── Plants ────────────────────────────────────────────────────────────────
  list: () => request<Plant[]>(BASE),
  get: (id: string) => request<Plant>(`${BASE}/${id}`),

  createWithPhoto: (
    data: {
      name: string;
      species?: string;
      common_name?: string;
      watering_interval_days?: number;
      sunlight?: SunlightLevel;
      notes?: string;
      room_id?: string;
    },
    photo?: File,
  ): Promise<Plant> => {
    const form = new FormData();
    form.append("name", data.name);
    if (data.species) form.append("species", data.species);
    if (data.common_name) form.append("common_name", data.common_name);
    if (data.watering_interval_days != null)
      form.append("watering_interval_days", String(data.watering_interval_days));
    if (data.sunlight) form.append("sunlight", data.sunlight);
    if (data.notes) form.append("notes", data.notes);
    if (data.room_id) form.append("room_id", data.room_id);
    if (photo) form.append("photo", photo);
    return request<Plant>(BASE, { method: "POST", body: form });
  },

  update: (id: string, data: PlantUpdate) =>
    json<Plant>(`${BASE}/${id}`, "PUT", data),

  patch: (id: string, data: PlantUpdate) =>
    json<Plant>(`${BASE}/${id}`, "PATCH", data),

  delete: (id: string) => request<void>(`${BASE}/${id}`, { method: "DELETE" }),

  identifyImage: (id: string, file: File, organ = "auto"): Promise<IdentifyResponse> => {
    const form = new FormData();
    form.append("image", file);
    form.append("organ", organ);
    return request<IdentifyResponse>(`${BASE}/${id}/identify`, { method: "POST", body: form });
  },

  identifyNew: (images: File[]): Promise<IdentifyNewResponse> => {
    const form = new FormData();
    images.forEach((img) => form.append("images", img));
    return request<IdentifyNewResponse>(`${BASE}/identify-new`, { method: "POST", body: form });
  },

  water: (id: string) =>
    request<WaterResponse>(`${BASE}/${id}/water`, { method: "POST" }),

  logCare: (id: string, action: string, notes?: string) =>
    json<CareLogEntry>(`${BASE}/${id}/care-log`, "POST", { action, notes }),

  getCareLog: (id: string) => request<CareLogEntry[]>(`${BASE}/${id}/care-log`),

  getSchedule: (dueToday = false) =>
    request<ScheduledPlant[]>(`/schedule${dueToday ? "?due_today=true" : ""}`),

  // ── Rooms ─────────────────────────────────────────────────────────────────
  listRooms: () => request<Room[]>("/rooms"),

  createRoom: (data: { name: string; icon?: string }) =>
    json<Room>("/rooms", "POST", data),
};
