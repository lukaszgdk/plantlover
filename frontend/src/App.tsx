import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { PlantList } from "./components/PlantList";
import { PlantDetail } from "./components/PlantDetail";
import { AddPlantForm } from "./components/AddPlantForm";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <header className="app-header">
        <a href="/" className="app-logo">
          🌿 PlantLover
        </a>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/plants" replace />} />
          <Route path="/plants" element={<PlantList />} />
          <Route path="/plants/new" element={<AddPlantForm />} />
          <Route path="/plants/:id" element={<PlantDetail />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
