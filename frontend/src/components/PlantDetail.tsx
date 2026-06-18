import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api/plants";
import { PhotoCapture } from "./PhotoCapture";
import type { IdentifyResponse, Plant, Room } from "../types/plant";

export function PlantDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [plant, setPlant] = useState<Plant | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [careMsg, setCareMsg] = useState<string | null>(null);
  const [watering, setWatering] = useState(false);
  const [savingRoom, setSavingRoom] = useState(false);
  const [fetchingInfo, setFetchingInfo] = useState(false);

  useEffect(() => {
    if (!id) return;
    Promise.all([api.get(id), api.listRooms()])
      .then(([p, r]) => {
        setPlant(p);
        setRooms(r);
      })
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
    setWatering(true);
    try {
      await api.water(plant.id);
      const updated = await api.get(plant.id);
      setPlant(updated);
      setCareMsg("Watered! ✅");
      setTimeout(() => setCareMsg(null), 3000);
    } catch (e) {
      setCareMsg((e as Error).message);
    } finally {
      setWatering(false);
    }
  }

  async function handleRoomChange(newRoomId: string) {
    if (!plant) return;
    setSavingRoom(true);
    try {
      const updated = await api.patch(plant.id, {
        room_id: newRoomId || undefined,
      });
      setPlant(updated);
    } catch (e) {
      setCareMsg((e as Error).message);
    } finally {
      setSavingRoom(false);
    }
  }

  function handleIdentified(result: IdentifyResponse) {
    if (!plant) return;
    setPlant({ ...plant, species: result.species, common_name: result.common_name });
  }

  async function handleFetchInfo() {
    if (!plant) return;
    setFetchingInfo(true);
    setCareMsg(null);
    try {
      const updated = await api.fetchInfo(plant.id);
      setPlant(updated);
      setCareMsg("✅ Informacje o roślinie pobrane!");
      setTimeout(() => setCareMsg(null), 3000);
    } catch (e) {
      setCareMsg(`❌ ${(e as Error).message}`);
    } finally {
      setFetchingInfo(false);
    }
  }

  function parsePlantInfo(raw: string | null) {
    if (!raw) return null;
    try { return JSON.parse(raw); } catch { return null; }
  }

  if (loading) return <p className="status">Loading…</p>;
  if (error) return <p className="status error">{error}</p>;
  if (!plant) return null;

  const lastWateredDisplay = plant.last_watered
    ? new Date(plant.last_watered).toLocaleString()
    : null;
  const nextWateringDisplay = plant.next_watering
    ? new Date(plant.next_watering).toLocaleDateString()
    : null;

  return (
    <div className="detail-page">
      <div className="page-header">
        <h1>{plant.name}</h1>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => navigate(-1)}>
            ← Back
          </button>
          <button className="btn btn-secondary" onClick={() => navigate(`/plants/${plant.id}/edit`)}>
            ✏️ Edit
          </button>
          <button className="btn btn-danger" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>

      <div className="detail-body">
        <div className="detail-photo-col">
          <div className="detail-photo">
            {plant.photo_url ? (
              <img src={plant.photo_url} alt={plant.name} />
            ) : (
              <span className="photo-placeholder large">🌿</span>
            )}
          </div>

          {plant.user_photo_url && (
            <div className="detail-gallery">
              <p className="gallery-label">📷 Twoje zdjęcie</p>
              <img src={plant.user_photo_url} alt="Zdjęcie użytkownika" className="gallery-thumb" />
            </div>
          )}
        </div>

        <div className="detail-info">
          <dl>
            {plant.species && (
              <>
                <dt>Species</dt>
                <dd>
                  <span>{plant.species}</span>
                  {plant.common_name && (
                    <span style={{ color: "var(--gray)", fontStyle: "italic" }}>
                      {" "}({plant.common_name})
                    </span>
                  )}
                  <button
                    className="btn-wiki-fetch"
                    onClick={handleFetchInfo}
                    disabled={fetchingInfo}
                    title="Pobierz informacje o roślinie z Perenual"
                  >
                    {fetchingInfo ? "…" : plant.plant_info ? "🔄" : "🔍 Pobierz info"}
                  </button>
                </dd>
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
            {lastWateredDisplay && (
              <>
                <dt>Last watered</dt>
                <dd>{lastWateredDisplay}</dd>
              </>
            )}
            {nextWateringDisplay && (
              <>
                <dt>Next watering</dt>
                <dd>{nextWateringDisplay}</dd>
              </>
            )}
            <dt>Added</dt>
            <dd>{new Date(plant.created_at).toLocaleDateString()}</dd>

            <dt>Room</dt>
            <dd>
              <select
                value={plant.room_id ?? ""}
                onChange={(e) => handleRoomChange(e.target.value)}
                disabled={savingRoom}
                style={{ fontSize: "inherit" }}
              >
                <option value="">— no room —</option>
                {rooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.icon} {r.name}
                  </option>
                ))}
              </select>
            </dd>
          </dl>

          {plant.notes && (
            <div className="notes">
              <h3>Notes</h3>
              <p>{plant.notes}</p>
            </div>
          )}

          <div className="care-actions">
            <button
              className="btn btn-primary"
              onClick={handleWater}
              disabled={watering}
            >
              {watering ? "Watering…" : "💧 Mark as watered"}
            </button>
          </div>
          {careMsg && <p className="status">{careMsg}</p>}

          <div style={{ marginTop: "1.5rem" }}>
            <PhotoCapture plantId={plant.id} onIdentified={handleIdentified} />
          </div>
        </div>
      </div>

      {(() => {
        const info = parsePlantInfo(plant.plant_info);
        if (!info) return null;
        const rows: { label: string; value: string }[] = [];
        if (info.origin?.length) rows.push({ label: "🌍 Pochodzenie", value: info.origin.join(", ") });
        if (info.cycle) rows.push({ label: "🔄 Cykl życia", value: info.cycle });
        if (info.type) rows.push({ label: "🌱 Typ", value: info.type });
        if (info.sunlight?.length) rows.push({ label: "☀️ Nasłonecznienie", value: info.sunlight.join(", ") });
        if (info.watering) rows.push({ label: "💧 Podlewanie", value: info.watering });
        if (info.soil?.length) rows.push({ label: "🪨 Gleba", value: info.soil.join(", ") });
        if (info.maintenance) rows.push({ label: "🔧 Pielęgnacja", value: info.maintenance });
        if (info.care_level) rows.push({ label: "📊 Poziom trudności", value: info.care_level });
        if (info.growth_rate) rows.push({ label: "📈 Tempo wzrostu", value: info.growth_rate });
        if (info.drought_tolerant != null) rows.push({ label: "🏜️ Tolerancja suszy", value: info.drought_tolerant ? "Tak" : "Nie" });
        if (info.indoor != null) rows.push({ label: "🏠 Roślina doniczkowa", value: info.indoor ? "Tak" : "Nie" });
        return (
          <div className="plant-info-card">
            <div className="plant-info-header">
              <h3>📋 Informacje o gatunku</h3>
              <button className="btn-wiki-fetch" onClick={handleFetchInfo} disabled={fetchingInfo}>
                {fetchingInfo ? "…" : "🔄"}
              </button>
            </div>
            <dl className="plant-info-grid">
              {rows.map(({ label, value }) => (
                <div key={label} className="plant-info-row">
                  <dt>{label}</dt>
                  <dd>{value}</dd>
                </div>
              ))}
            </dl>
            {info.description && (
              <p className="plant-info-description">{info.description}</p>
            )}
          </div>
        );
      })()}

    </div>
  );
}
