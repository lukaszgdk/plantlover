import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import type { EventClickArg } from "@fullcalendar/core";
import { api } from "../api/plants";
import type { ScheduledPlant } from "../types/plant";

function eventColor(plant: ScheduledPlant): string {
  if (!plant.last_watered) return "#c1121f"; // never watered → always red
  if (!plant.next_watering) return "#40916c";
  const now = new Date();
  const nextWatering = new Date(plant.next_watering);
  const todayEnd = new Date(now);
  todayEnd.setHours(23, 59, 59, 999);

  const lastWatered = new Date(plant.last_watered);
  const todayStart = new Date(now);
  todayStart.setHours(0, 0, 0, 0);
  if (lastWatered >= todayStart) return "#40916c";
  if (nextWatering < now) return "#c1121f";
  if (nextWatering <= todayEnd) return "#e07c24";
  return "#40916c";
}

function eventTitle(plant: ScheduledPlant): string {
  const roomPrefix = plant.room ? `${plant.room.icon ?? ""} ` : "";
  return `${roomPrefix}${plant.name}`;
}

export function WateringCalendar() {
  const [plants, setPlants] = useState<ScheduledPlant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .getSchedule()
      .then(setPlants)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const events = plants
    .filter((p) => p.next_watering)
    .map((p) => ({
      id: p.id,
      title: eventTitle(p),
      date: p.next_watering!.split("T")[0],
      backgroundColor: eventColor(p),
      borderColor: eventColor(p),
      extendedProps: { plantId: p.id },
    }));

  function handleEventClick(info: EventClickArg) {
    navigate(`/plants/${info.event.extendedProps.plantId}`);
  }

  if (loading) return <p className="status">Loading schedule…</p>;
  if (error) return <p className="status error">Error: {error}</p>;

  return (
    <div>
      <div className="page-header">
        <h1>Watering Schedule</h1>
      </div>
      <div className="calendar-legend">
        <span className="legend-dot" style={{ background: "#40916c" }} /> Watered today / upcoming
        <span className="legend-dot" style={{ background: "#e07c24", marginLeft: "1rem" }} /> Due today
        <span className="legend-dot" style={{ background: "#c1121f", marginLeft: "1rem" }} /> Overdue
      </div>
      <FullCalendar
        plugins={[dayGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        events={events}
        eventClick={handleEventClick}
        height="auto"
        headerToolbar={{
          left: "prev,next today",
          center: "title",
          right: "dayGridMonth",
        }}
      />
      {plants.length === 0 && (
        <p className="status" style={{ marginTop: "1rem" }}>
          No plants scheduled yet. Set a watering interval and mark a plant as watered.
        </p>
      )}
    </div>
  );
}
