import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/plants";
import type { PlantCreate, SunlightLevel } from "../types/plant";

export function AddPlantForm() {
  const navigate = useNavigate();
  const [form, setForm] = useState<PlantCreate>({ name: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set(field: keyof PlantCreate, value: string | number | undefined) {
    setForm((f) => ({ ...f, [field]: value || undefined }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const plant = await api.create(form);
      navigate(`/plants/${plant.id}`);
    } catch (err) {
      setError((err as Error).message);
      setSubmitting(false);
    }
  }

  return (
    <div className="form-page">
      <div className="page-header">
        <h1>Add Plant</h1>
        <button className="btn btn-secondary" onClick={() => navigate(-1)}>
          Cancel
        </button>
      </div>
      <form onSubmit={handleSubmit} className="plant-form">
        <label>
          Name <span className="required">*</span>
          <input
            required
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
            placeholder="e.g. Kitchen Monstera"
          />
        </label>
        <label>
          Species
          <input
            value={form.species ?? ""}
            onChange={(e) => set("species", e.target.value)}
            placeholder="e.g. Monstera deliciosa"
          />
        </label>
        <label>
          Photo URL
          <input
            type="url"
            value={form.photo_url ?? ""}
            onChange={(e) => set("photo_url", e.target.value)}
            placeholder="https://…"
          />
        </label>
        <label>
          Sunlight
          <select
            value={form.sunlight ?? ""}
            onChange={(e) => set("sunlight", e.target.value as SunlightLevel)}
          >
            <option value="">— select —</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
        <label>
          Watering interval (days)
          <input
            type="number"
            min={1}
            value={form.watering_interval_days ?? ""}
            onChange={(e) =>
              set("watering_interval_days", e.target.value ? Number(e.target.value) : undefined)
            }
          />
        </label>
        <label>
          Notes
          <textarea
            rows={4}
            value={form.notes ?? ""}
            onChange={(e) => set("notes", e.target.value)}
          />
        </label>
        {error && <p className="status error">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Saving…" : "Save Plant"}
        </button>
      </form>
    </div>
  );
}
