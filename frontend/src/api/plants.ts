import type {
  Achievement,
  AppConfig,
  CareLogEntry,
  IdentifyNewResponse,
  IdentifyResponse,
  Plant,
  PlantUpdate,
  Room,
  ScheduledPlant,
  SpeciesCare,
  SunlightLevel,
  WaterResponse,
} from "../types/plant";

const BASE = "/api/plants";

// Simple TTL cache for data that rarely changes within a session
const _cache = new Map<string, { data: unknown; expires: number }>();

function cached<T>(key: string, ttlMs: number, fn: () => Promise<T>): Promise<T> {
  const hit = _cache.get(key);
  if (hit && hit.expires > Date.now()) return Promise.resolve(hit.data as T);
  return fn().then((data) => {
    _cache.set(key, { data, expires: Date.now() + ttlMs });
    return data;
  });
}

export function invalidateCache(...keys: string[]) {
  keys.forEach((k) => _cache.delete(k));
}

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
  list: () => cached<Plant[]>("plants", 10_000, () => request<Plant[]>(BASE)),
  get: (id: string) => cached<Plant>(`plant:${id}`, 10_000, () => request<Plant>(`${BASE}/${id}`)),

  createWithPhoto: (
    data: {
      name: string;
      species?: string;
      common_name?: string;
      watering_interval_days?: number;
      sunlight?: SunlightLevel;
      notes?: string;
      room_id?: string;
      photo_url?: string;
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
    if (data.photo_url) form.append("photo_url", data.photo_url);
    if (photo) form.append("photo", photo);
    return request<Plant>(BASE, { method: "POST", body: form }).then((r) => { invalidateCache("plants"); return r; });
  },

  update: (id: string, data: PlantUpdate) =>
    json<Plant>(`${BASE}/${id}`, "PUT", data).then((r) => { invalidateCache("plants", `plant:${id}`); return r; }),

  patch: (id: string, data: PlantUpdate) =>
    json<Plant>(`${BASE}/${id}`, "PATCH", data).then((r) => { invalidateCache("plants", `plant:${id}`); return r; }),

  delete: (id: string) =>
    request<void>(`${BASE}/${id}`, { method: "DELETE" }).then((r) => { invalidateCache("plants", `plant:${id}`); return r; }),

  fetchInfo: (id: string) =>
    request<Plant>(`${BASE}/${id}/fetch-info`, { method: "POST" }).then((r) => { invalidateCache("plants", `plant:${id}`); return r; }),

  getAchievements: () => cached<Achievement[]>("achievements", 60_000, () => request<Achievement[]>("/api/achievements")),

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
    request<WaterResponse>(`${BASE}/${id}/water`, { method: "POST" }).then((r) => { invalidateCache("plants", `plant:${id}`, "achievements"); return r; }),

  logCare: (id: string, action: string, notes?: string) =>
    json<CareLogEntry>(`${BASE}/${id}/care-log`, "POST", { action, notes }),

  getCareLog: (id: string) => request<CareLogEntry[]>(`${BASE}/${id}/care-log`),

  getSchedule: (dueToday = false) =>
    request<ScheduledPlant[]>(`/api/schedule${dueToday ? "?due_today=true" : ""}`),

  getSpeciesCare: (species: string) =>
    request<SpeciesCare>(`/api/plants/species-care?species=${encodeURIComponent(species)}`),

  // ── Rooms ─────────────────────────────────────────────────────────────────
  listRooms: () => cached<Room[]>("rooms", 60_000, () => request<Room[]>("/api/rooms")),

  createRoom: (data: { name: string; icon?: string }) =>
    json<Room>("/api/rooms", "POST", data).then((r) => { invalidateCache("rooms"); return r; }),

  deleteRoom: (id: string) =>
    request<void>(`/api/rooms/${id}`, { method: "DELETE" }).then((r) => { invalidateCache("rooms"); return r; }),

  // ── Config / Setup ────────────────────────────────────────────────────────
  getSetupStatus: () => request<{ completed: boolean }>("/api/config/status"),

  getConfig: () => request<AppConfig>("/api/config"),

  saveConfig: (data: Partial<{
    plantnet_api_key: string;
    discord_bot_token: string;
    discord_channel_id: string;
    reminder_times: string[];
    setup_completed: boolean;
  }>) => json<{ ok: boolean }>("/api/config", "PUT", data),

  completeSetup: () => request<{ ok: boolean }>("/api/config/complete-setup", { method: "POST" }),
};
