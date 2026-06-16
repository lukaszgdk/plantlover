import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/plants";
import type { Plant } from "../types/plant";

export function PlantDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [plant, setPlant] = useState<Plant | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [careMsg, setCareMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api
      .get(id)
      .then(setPlant)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  async function handleDelete() {
    if (!plant) return;
    if (!confirm(`Delete "${plant.name}"?`)) return;
    await api.delete(plant.id);
    navigate("/");
  }

  async function handleWater() {
    if (!plant) return;
    try {
      await api.logCare(plant.id, "watering");
      const updated = await api.get(plant.id);
      setPlant(updated);
      setCareMsg("Watering logged!");
      setTimeout(() => setCareMsg(null), 3000);
    } catch (e) {
      setCareMsg((e as Error).message);
    }
  }

  if (loading) return <p className="status">Loading…</p>;
  if (error) return <p className="status error">{error}</p>;
  if (!plant) return null;

  return (
    <div className="detail-page">
      <div className="page-header">
        <h1>{plant.name}</h1>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => navigate(-1)}>
            ← Back
          </button>
          <button className="btn btn-danger" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>

      <div className="detail-body">
        <div className="detail-photo">
          {plant.photo_url ? (
            <img src={plant.photo_url} alt={plant.name} />
          ) : (
            <span className="photo-placeholder large">🌿</span>
          )}
        </div>

        <div className="detail-info">
          <dl>
            {plant.species && (
              <>
                <dt>Species</dt>
                <dd>{plant.species}</dd>
              </>
            )}
            {plant.sunlight && (
              <>
                <dt>Sunlight</dt>
                <dd className={`sunlight sunlight-${plant.sunlight}`}>{plant.sunlight}</dd>
              </>
            )}
            {plant.watering_interval_days && (
              <>
                <dt>Watering every</dt>
                <dd>{plant.watering_interval_days} days</dd>
              </>
            )}
            {plant.last_watered && (
              <>
                <dt>Last watered</dt>
                <dd>{plant.last_watered}</dd>
              </>
            )}
            <dt>Added</dt>
            <dd>{new Date(plant.created_at).toLocaleDateString()}</dd>
          </dl>

          {plant.notes && (
            <div className="notes">
              <h3>Notes</h3>
              <p>{plant.notes}</p>
            </div>
          )}

          <div className="care-actions">
            <button className="btn btn-primary" onClick={handleWater}>
              💧 Log Watering
            </button>
          </div>
          {careMsg && <p className="status">{careMsg}</p>}
        </div>
      </div>
    </div>
  );
}
