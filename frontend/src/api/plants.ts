import type { Plant, PlantCreate, PlantUpdate } from "../types/plant";

const BASE = "/plants";

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  list: () => request<Plant[]>(BASE),
  get: (id: string) => request<Plant>(`${BASE}/${id}`),
  create: (data: PlantCreate) =>
    request<Plant>(BASE, { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: PlantUpdate) =>
    request<Plant>(`${BASE}/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`${BASE}/${id}`, { method: "DELETE" }),
  identify: (id: string, imageBase64: string) =>
    request(`${BASE}/${id}/identify`, {
      method: "POST",
      body: JSON.stringify({ image_base64: imageBase64 }),
    }),
  logCare: (id: string, eventType: "watering" | "fertilizing", notes?: string) =>
    request(`${BASE}/${id}/care-log`, {
      method: "POST",
      body: JSON.stringify({ event_type: eventType, notes }),
    }),
};
