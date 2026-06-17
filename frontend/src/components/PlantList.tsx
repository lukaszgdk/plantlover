import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/plants";
import { PlantCard } from "./PlantCard";
import type { Plant, Room } from "../types/plant";

export function PlantList() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.list(), api.listRooms()])
      .then(([p, r]) => {
        setPlants(p);
        setRooms(r);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function handleWatered(updated: Plant) {
    setPlants((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
  }

  const filtered =
    selectedRoomId === "__none__"
      ? plants.filter((p) => !p.room_id)
      : selectedRoomId
        ? plants.filter((p) => p.room_id === selectedRoomId)
        : plants;

  if (loading) return <p className="status">Loading plants…</p>;
  if (error) return <p className="status error">Error: {error}</p>;

  return (
    <div>
      <div className="page-header">
        <h1>My Plants</h1>
        <Link to="/plants/new" className="btn btn-primary">
          + Add Plant
        </Link>
      </div>

      {rooms.length > 0 && (
        <div className="room-tabs">
          <button
            className={`room-tab${selectedRoomId === null ? " active" : ""}`}
            onClick={() => setSelectedRoomId(null)}
          >
            All ({plants.length})
          </button>
          {rooms.map((r) => {
            const count = plants.filter((p) => p.room_id === r.id).length;
            return (
              <button
                key={r.id}
                className={`room-tab${selectedRoomId === r.id ? " active" : ""}`}
                onClick={() => setSelectedRoomId(r.id)}
              >
                {r.icon} {r.name} ({count})
              </button>
            );
          })}
          <button
            className={`room-tab${selectedRoomId === "__none__" ? " active" : ""}`}
            onClick={() => setSelectedRoomId("__none__")}
          >
            No room ({plants.filter((p) => !p.room_id).length})
          </button>
        </div>
      )}

      {filtered.length === 0 ? (
        <p className="status">No plants here yet.</p>
      ) : (
        <div className="plant-grid">
          {filtered.map((p) => (
            <PlantCard key={p.id} plant={p} onWatered={handleWatered} />
          ))}
        </div>
      )}
    </div>
  );
}
