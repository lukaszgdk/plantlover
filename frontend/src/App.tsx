import { BrowserRouter, Routes, Route, Navigate, NavLink } from "react-router-dom";
import { PlantList } from "./components/PlantList";
import { PlantDetail } from "./components/PlantDetail";
import { AddPlantForm } from "./components/AddPlantForm";
import { EditPlantForm } from "./components/EditPlantForm";
import { WateringCalendar } from "./components/WateringCalendar";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <header className="app-header">
        <a href="/" className="app-logo">
          🌿 PlantLover
        </a>
        <nav className="app-nav">
          <NavLink to="/plants" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Plants
          </NavLink>
          <NavLink to="/calendar" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Calendar
          </NavLink>
        </nav>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/plants" replace />} />
          <Route path="/plants" element={<PlantList />} />
          <Route path="/plants/new" element={<AddPlantForm />} />
          <Route path="/plants/:id/edit" element={<EditPlantForm />} />
          <Route path="/plants/:id" element={<PlantDetail />} />
          <Route path="/calendar" element={<WateringCalendar />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
