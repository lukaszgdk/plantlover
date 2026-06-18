import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/plants";
import type { Plant } from "../types/plant";

interface Props {
  plant: Plant;
  onWatered?: (updated: Plant) => void;
}

export function PlantCard({ plant, onWatered }: Props) {
  const [watering, setWatering] = useState(false);

  async function handleWater(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    setWatering(true);
    try {
      await api.water(plant.id);
      const updated = await api.get(plant.id);
      onWatered?.(updated);
    } finally {
      setWatering(false);
    }
  }

  const displayDate = plant.last_watered
    ? new Date(plant.last_watered).toLocaleDateString()
    : null;

  return (
    <Link to={`/plants/${plant.id}`} style={{ textDecoration: "none", color: "inherit" }}>
      <div className="plant-card">
        <div className="plant-card-photo">
          {plant.photo_url ? (
            <img src={plant.photo_url} alt={plant.name} loading="lazy" decoding="async" />
          ) : (
            <span className="photo-placeholder">🌿</span>
          )}
        </div>
        <div className="plant-card-body">
          <h3>{plant.name}</h3>
          {plant.species && <p className="species">{plant.species}</p>}
          <div className="plant-card-meta">
            {plant.sunlight && (
              <span className={`sunlight sunlight-${plant.sunlight}`}>{plant.sunlight}</span>
            )}
            {displayDate ? (
              <span className="last-watered">Watered {displayDate}</span>
            ) : (
              <span className="never-watered">
                <span className="never-watered-dot" />
                Never watered
              </span>
            )}
          </div>
          <button
            className="btn btn-primary btn-water"
            onClick={handleWater}
            disabled={watering}
          >
            {watering ? "…" : "💧"}
          </button>
        </div>
      </div>
    </Link>
  );
}
