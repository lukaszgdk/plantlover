import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, NavLink, useNavigate, useLocation } from "react-router-dom";
import { PlantList } from "./components/PlantList";
import { PlantDetail } from "./components/PlantDetail";
import { AddPlantForm } from "./components/AddPlantForm";
import { EditPlantForm } from "./components/EditPlantForm";
import { WateringCalendar } from "./components/WateringCalendar";
import { SetupWizard } from "./components/SetupWizard";
import { SettingsPage } from "./components/SettingsPage";
import AchievementsPage from "./components/AchievementsPage";
import { api } from "./api/plants";
import "./index.css";

function AppShell() {
  const navigate = useNavigate();
  const location = useLocation();
  const [setupChecked, setSetupChecked] = useState(false);

  useEffect(() => {
    if (location.pathname === "/setup") { setSetupChecked(true); return; }
    api.getSetupStatus()
      .then(({ completed }) => {
        if (!completed) navigate("/setup", { replace: true });
      })
      .catch(() => {})
      .finally(() => setSetupChecked(true));
  }, []);

  if (!setupChecked && location.pathname !== "/setup") return null;

  const isSetup = location.pathname === "/setup";

  return (
    <>
      {!isSetup && (
        <header className="app-header">
          <a href="/" className="app-logo">🌿 PlantLover</a>
          <nav className="app-nav">
            <NavLink to="/plants" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Plants
            </NavLink>
            <NavLink to="/calendar" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Calendar
            </NavLink>
            <NavLink to="/achievements" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              🏅
            </NavLink>
            <NavLink to="/settings" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              ⚙️
            </NavLink>
          </nav>
        </header>
      )}
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/plants" replace />} />
          <Route path="/setup" element={<SetupWizard />} />
          <Route path="/plants" element={<PlantList />} />
          <Route path="/plants/new" element={<AddPlantForm />} />
          <Route path="/plants/:id/edit" element={<EditPlantForm />} />
          <Route path="/plants/:id" element={<PlantDetail />} />
          <Route path="/calendar" element={<WateringCalendar />} />
          <Route path="/achievements" element={<AchievementsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
