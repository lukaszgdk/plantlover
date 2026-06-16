import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/plants";
import { PlantCard } from "./PlantCard";
import type { Plant } from "../types/plant";

export function PlantList() {
  const [plants, setPlants] = useState<Plant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .list()
      .then(setPlants)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

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
      {plants.length === 0 ? (
        <p className="status">No plants yet. Add your first one!</p>
      ) : (
        <div className="plant-grid">
          {plants.map((p) => (
            <PlantCard key={p.id} plant={p} />
          ))}
        </div>
      )}
    </div>
  );
}
