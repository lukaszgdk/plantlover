export type SunlightLevel = "low" | "medium" | "high";

export interface Room {
  id: string;
  name: string;
  icon: string | null;
}

export interface Plant {
  id: string;
  name: string;
  species: string | null;
  common_name: string | null;
  photo_url: string | null;
  user_photo_url: string | null;
  wiki_url: string | null;
  watering_interval_days: number | null;
  last_watered: string | null;
  next_watering: string | null;
  sunlight: SunlightLevel | null;
  notes: string | null;
  created_at: string;
  room_id: string | null;
  room: Room | null;
}

export interface PlantCreate {
  name: string;
  species?: string;
  common_name?: string;
  photo_url?: string;
  watering_interval_days?: number;
  last_watered?: string;
  sunlight?: SunlightLevel;
  notes?: string;
  room_id?: string;
}

export interface PlantUpdate extends Partial<PlantCreate> {}

export interface IdentifyResult {
  species: string;
  common_name: string | null;
  score: number;
  reference_image_url: string | null;
  gbif_id: string | null;
}

export interface SpeciesCare {
  watering_days: number | null;
  sunlight: string | null;
  source: "database" | "not_found";
}

export interface AppConfig {
  setup_completed: boolean;
  plantnet_api_key_set: boolean;
  perenual_api_key_set: boolean;
  discord_bot_token_set: boolean;
  discord_channel_id: string | null;
  reminder_times: string[];
}

export interface IdentifyResponse {
  species: string;
  common_name: string | null;
  score: number;
  all_results: IdentifyResult[];
}

export interface IdentifyNewResponse {
  top: IdentifyResult;
  alternatives: IdentifyResult[];
}

export interface WaterResponse {
  plant_id: string;
  last_watered: string;
  next_watering: string | null;
}

export interface ScheduledPlant {
  id: string;
  name: string;
  species: string | null;
  photo_url: string | null;
  next_watering: string | null;
  last_watered: string | null;
  room: Room | null;
}

export interface CareLogEntry {
  id: string;
  plant_id: string;
  logged_at: string;
  action: string;
  notes: string | null;
}
