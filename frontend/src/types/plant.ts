export type SunlightLevel = "low" | "medium" | "high";

export interface Plant {
  id: string;
  name: string;
  species: string | null;
  photo_url: string | null;
  watering_interval_days: number | null;
  last_watered: string | null;
  sunlight: SunlightLevel | null;
  notes: string | null;
  created_at: string;
}

export interface PlantCreate {
  name: string;
  species?: string;
  photo_url?: string;
  watering_interval_days?: number;
  last_watered?: string;
  sunlight?: SunlightLevel;
  notes?: string;
}

export interface PlantUpdate extends Partial<PlantCreate> {}
