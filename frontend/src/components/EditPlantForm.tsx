import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/plants";
import type { Plant, Room, SunlightLevel } from "../types/plant";

export function EditPlantForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [plant, setPlant] = useState<Plant | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // form fields
  const [name, setName] = useState("");
  const [species, setSpecies] = useState("");
  const [commonName, setCommonName] = useState("");
  const [roomId, setRoomId] = useState("");
  const [wateringDays, setWateringDays] = useState<number | "">("");
  const [sunlight, setSunlight] = useState<SunlightLevel | "">("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!id) return;
    Promise.all([api.get(id), api.listRooms()])
      .then(([p, r]) => {
        setPlant(p);
        setRooms(r);
        setName(p.name);
        setSpecies(p.species ?? "");
        setCommonName(p.common_name ?? "");
        setRoomId(p.room_id ?? "");
        setWateringDays(p.watering_interval_days ?? "");
        setSunlight(p.sunlight ?? "");
        setNotes(p.notes ?? "");
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!plant) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.update(plant.id, {
        name,
        species: species || undefined,
        common_name: commonName || undefined,
        room_id: roomId || undefined,
        watering_interval_days: wateringDays !== "" ? Number(wateringDays) : undefined,
        sunlight: sunlight || undefined,
        notes: notes || undefined,
      });
      navigate(`/plants/${plant.id}`);
    } catch (e) {
      setError((e as Error).message);
      setSubmitting(false);
    }
  }

  if (loading) return <p className="status">Loading…</p>;
  if (error && !plant) return <p className="status error">{error}</p>;
  if (!plant) return null;

  return (
    <div className="form-page">
      <div className="page-header">
        <h1>Edit plant</h1>
        <button className="btn btn-secondary" onClick={() => navigate(-1)}>
          Cancel
        </button>
      </div>

      {plant.photo_url && (
        <img
          src={plant.photo_url}
          alt={plant.name}
          style={{ width: 80, height: 80, objectFit: "cover", borderRadius: 8, marginBottom: "1rem" }}
        />
      )}

      <form onSubmit={handleSubmit} className="plant-form">
        <label>
          Name <span className="required">*</span>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>

        <label>
          Species
          <input
            value={species}
            onChange={(e) => setSpecies(e.target.value)}
            placeholder="e.g. Monstera deliciosa"
          />
        </label>

        <label>
          Common name
          <input
            value={commonName}
            onChange={(e) => setCommonName(e.target.value)}
          />
        </label>

        <label>
          Room
          <select value={roomId} onChange={(e) => setRoomId(e.target.value)}>
            <option value="">— no room —</option>
            {rooms.map((r) => (
              <option key={r.id} value={r.id}>
                {r.icon} {r.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Watering interval (days)
          <input
            type="number"
            min={1}
            value={wateringDays}
            onChange={(e) =>
              setWateringDays(e.target.value ? Number(e.target.value) : "")
            }
          />
        </label>

        <label>
          Sunlight
          <select
            value={sunlight}
            onChange={(e) => setSunlight(e.target.value as SunlightLevel | "")}
          >
            <option value="">— select —</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>

        <label>
          Notes
          <textarea
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </label>

        {error && <p className="status error">{error}</p>}

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Saving…" : "Save changes"}
        </button>
      </form>
    </div>
  );
}
