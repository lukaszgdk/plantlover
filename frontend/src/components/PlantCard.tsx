import { Link } from "react-router-dom";
import type { Plant } from "../types/plant";

interface Props {
  plant: Plant;
}

export function PlantCard({ plant }: Props) {
  return (
    <Link to={`/plants/${plant.id}`} style={{ textDecoration: "none", color: "inherit" }}>
      <div className="plant-card">
        <div className="plant-card-photo">
          {plant.photo_url ? (
            <img src={plant.photo_url} alt={plant.name} />
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
            {plant.last_watered && (
              <span className="last-watered">Watered {plant.last_watered}</span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
