import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/plants";
import type { Room } from "../types/plant";

type Step = "welcome" | "rooms" | "plantnet" | "discord" | "done";

const ROOM_ICONS = ["🛋️", "🛏️", "🚿", "🍳", "🪟", "🌿", "🏡", "📚", "🪴", "💼"];

export function SetupWizard() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>("welcome");

  // Rooms
  const [rooms, setRooms] = useState<Room[]>([]);
  const [roomName, setRoomName] = useState("");
  const [roomIcon, setRoomIcon] = useState("🌿");
  const [roomError, setRoomError] = useState<string | null>(null);
  const [addingRoom, setAddingRoom] = useState(false);

  // PlantNet
  const [plantnetKey, setPlantnetKey] = useState("");
  const [plantnetSaved, setPlantnetSaved] = useState(false);
  const [plantnetError, setPlantnetError] = useState<string | null>(null);
  const [plantnetSaving, setPlantnetSaving] = useState(false);

  // Discord
  const [discordToken, setDiscordToken] = useState("");
  const [discordChannel, setDiscordChannel] = useState("");
  const [discordSaved, setDiscordSaved] = useState(false);
  const [discordError, setDiscordError] = useState<string | null>(null);
  const [discordSaving, setDiscordSaving] = useState(false);
  const [reminderTimes, setReminderTimes] = useState<string[]>(["08:00", "15:00", "20:00"]);
  const [newTime, setNewTime] = useState("09:00");

  useEffect(() => {
    api.listRooms().then(setRooms).catch(() => {});
    api.getConfig().then((cfg) => {
      setPlantnetSaved(cfg.plantnet_api_key_set);
      setDiscordSaved(cfg.discord_bot_token_set);
      if (cfg.discord_channel_id) setDiscordChannel(cfg.discord_channel_id);
      if (cfg.reminder_times?.length) setReminderTimes(cfg.reminder_times);
    }).catch(() => {});
  }, []);

  async function addRoom() {
    if (!roomName.trim()) { setRoomError("Podaj nazwę pomieszczenia."); return; }
    setAddingRoom(true);
    setRoomError(null);
    try {
      const r = await api.createRoom({ name: roomName.trim(), icon: roomIcon });
      setRooms((prev) => [...prev, r]);
      setRoomName("");
      setRoomIcon("🌿");
    } catch {
      setRoomError("Błąd podczas dodawania pomieszczenia.");
    } finally {
      setAddingRoom(false);
    }
  }

  async function removeRoom(id: string) {
    try {
      await api.deleteRoom(id);
      setRooms((prev) => prev.filter((r) => r.id !== id));
    } catch {
      setRoomError("Nie można usunąć pomieszczenia (może mieć przypisane rośliny).");
    }
  }

  async function savePlantnet() {
    if (!plantnetKey.trim()) { setPlantnetError("Wpisz klucz API."); return; }
    setPlantnetSaving(true);
    setPlantnetError(null);
    try {
      await api.saveConfig({ plantnet_api_key: plantnetKey.trim() });
      setPlantnetSaved(true);
      setPlantnetKey("");
    } catch {
      setPlantnetError("Błąd zapisu.");
    } finally {
      setPlantnetSaving(false);
    }
  }

  async function saveDiscord() {
    setDiscordSaving(true);
    setDiscordError(null);
    try {
      await api.saveConfig({
        discord_bot_token: discordToken.trim() || undefined,
        discord_channel_id: discordChannel.trim() || undefined,
        reminder_times: reminderTimes,
      } as Parameters<typeof api.saveConfig>[0]);
      setDiscordSaved(true);
      setDiscordToken("");
    } catch {
      setDiscordError("Błąd zapisu.");
    } finally {
      setDiscordSaving(false);
    }
  }

  function addReminderTime() {
    if (!newTime || reminderTimes.includes(newTime)) return;
    const sorted = [...reminderTimes, newTime].sort();
    setReminderTimes(sorted);
  }

  function removeReminderTime(t: string) {
    if (reminderTimes.length <= 1) return;
    setReminderTimes(reminderTimes.filter((x) => x !== t));
  }

  async function finish() {
    await api.completeSetup();
    navigate("/plants");
  }

  // ── Welcome ────────────────────────────────────────────────────────────────
  if (step === "welcome") {
    return (
      <div className="setup-page">
        <div className="setup-card">
          <div className="setup-logo">🌿</div>
          <h1>Witaj w PlantLover!</h1>
          <p className="setup-subtitle">
            Skonfiguruj aplikację w kilku krokach — potrwa to mniej niż minutę.
          </p>
          <div className="setup-steps-preview">
            <span>🏠 Pomieszczenia</span>
            <span>→</span>
            <span>📷 PlantNet API</span>
            <span>→</span>
            <span>💬 Discord</span>
          </div>
          <button className="btn btn-primary setup-next" onClick={() => setStep("rooms")}>
            Zaczynamy →
          </button>
        </div>
      </div>
    );
  }

  // ── Rooms ──────────────────────────────────────────────────────────────────
  if (step === "rooms") {
    return (
      <div className="setup-page">
        <div className="setup-card">
          <div className="setup-step-indicator">Krok 1 / 3</div>
          <h2>🏠 Pomieszczenia</h2>
          <p className="setup-subtitle">
            Dodaj pomieszczenia w których trzymasz rośliny. Dzięki temu powiadomienia
            Discord będą grupowane per pokój.
          </p>

          <div className="setup-room-add">
            <div className="setup-icon-picker">
              {ROOM_ICONS.map((icon) => (
                <button
                  key={icon}
                  className={`icon-btn ${roomIcon === icon ? "selected" : ""}`}
                  onClick={() => setRoomIcon(icon)}
                  type="button"
                >
                  {icon}
                </button>
              ))}
            </div>
            <div className="setup-room-input-row">
              <span className="setup-selected-icon">{roomIcon}</span>
              <input
                value={roomName}
                onChange={(e) => setRoomName(e.target.value)}
                placeholder="Nazwa pomieszczenia (np. Salon)"
                onKeyDown={(e) => e.key === "Enter" && addRoom()}
              />
              <button className="btn btn-primary" onClick={addRoom} disabled={addingRoom}>
                + Dodaj
              </button>
            </div>
            {roomError && <p className="status error">{roomError}</p>}
          </div>

          {rooms.length > 0 && (
            <ul className="setup-room-list">
              {rooms.map((r) => (
                <li key={r.id} className="setup-room-item">
                  <span>{r.icon} {r.name}</span>
                  <button className="btn-icon-delete" onClick={() => removeRoom(r.id)} title="Usuń">×</button>
                </li>
              ))}
            </ul>
          )}

          <div className="setup-nav">
            <button className="btn btn-secondary" onClick={() => setStep("welcome")}>← Wstecz</button>
            <button className="btn btn-primary" onClick={() => setStep("plantnet")}>
              Dalej → {rooms.length === 0 && <span className="setup-skip">(pomiń)</span>}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── PlantNet ───────────────────────────────────────────────────────────────
  if (step === "plantnet") {
    return (
      <div className="setup-page">
        <div className="setup-card">
          <div className="setup-step-indicator">Krok 2 / 3</div>
          <h2>📷 PlantNet API</h2>
          <p className="setup-subtitle">
            PlantNet pozwala identyfikować rośliny ze zdjęcia. Klucz API uzyskasz
            bezpłatnie na{" "}
            <a href="https://my.plantnet.org" target="_blank" rel="noreferrer">
              my.plantnet.org
            </a>
            .
          </p>

          {plantnetSaved ? (
            <div className="setup-saved-badge">✅ Klucz API zapisany</div>
          ) : (
            <div className="setup-input-group">
              <input
                type="password"
                value={plantnetKey}
                onChange={(e) => setPlantnetKey(e.target.value)}
                placeholder="Wklej klucz API PlantNet"
                onKeyDown={(e) => e.key === "Enter" && savePlantnet()}
              />
              <button className="btn btn-primary" onClick={savePlantnet} disabled={plantnetSaving}>
                {plantnetSaving ? "Zapisuję…" : "Zapisz"}
              </button>
              {plantnetError && <p className="status error">{plantnetError}</p>}
            </div>
          )}

          <p className="setup-optional">Możesz to skonfigurować później w ustawieniach.</p>

          <div className="setup-nav">
            <button className="btn btn-secondary" onClick={() => setStep("rooms")}>← Wstecz</button>
            <button className="btn btn-primary" onClick={() => setStep("discord")}>
              Dalej →
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Discord ────────────────────────────────────────────────────────────────
  if (step === "discord") {
    return (
      <div className="setup-page">
        <div className="setup-card">
          <div className="setup-step-indicator">Krok 3 / 3</div>
          <h2>💬 Discord Bot</h2>
          <p className="setup-subtitle">
            Bot wysyła przypomnienia o podlewaniu na Discordzie i oznacza rośliny
            jako podlane gdy zareagujesz na wiadomość.
          </p>

          {discordSaved ? (
            <div className="setup-saved-badge">✅ Discord skonfigurowany</div>
          ) : (
            <div className="setup-input-group">
              <label>
                Token bota
                <input
                  type="password"
                  value={discordToken}
                  onChange={(e) => setDiscordToken(e.target.value)}
                  placeholder="Bot token z Discord Developer Portal"
                />
              </label>
              <label>
                ID kanału
                <input
                  value={discordChannel}
                  onChange={(e) => setDiscordChannel(e.target.value)}
                  placeholder="np. 1516900842588995704"
                />
              </label>
              <button className="btn btn-primary" onClick={saveDiscord} disabled={discordSaving}>
                {discordSaving ? "Zapisuję…" : "Zapisz"}
              </button>
              {discordError && <p className="status error">{discordError}</p>}
            </div>
          )}

          <div className="setup-reminder-times">
            <h3>🕐 Godziny przypomnień</h3>
            <p className="setup-subtitle" style={{ marginBottom: "0.5rem" }}>
              Bot sprawdzi rośliny do podlania o tych godzinach.
            </p>
            <div className="reminder-times-list">
              {reminderTimes.map((t) => (
                <span key={t} className="reminder-time-chip">
                  {t}
                  <button onClick={() => removeReminderTime(t)} disabled={reminderTimes.length <= 1}>×</button>
                </span>
              ))}
            </div>
            <div className="reminder-time-add">
              <input type="time" value={newTime} onChange={(e) => setNewTime(e.target.value)} />
              <button className="btn btn-secondary" onClick={addReminderTime}>+ Dodaj</button>
            </div>
          </div>

          <p className="setup-optional">Możesz to skonfigurować później w ustawieniach.</p>

          <div className="setup-nav">
            <button className="btn btn-secondary" onClick={() => setStep("plantnet")}>← Wstecz</button>
            <button className="btn btn-primary" onClick={() => setStep("done")}>
              Dalej →
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Done ───────────────────────────────────────────────────────────────────
  return (
    <div className="setup-page">
      <div className="setup-card setup-done">
        <div className="setup-logo">🎉</div>
        <h2>Wszystko gotowe!</h2>
        <div className="setup-summary">
          <div className={`setup-summary-item ${rooms.length > 0 ? "ok" : "skip"}`}>
            {rooms.length > 0 ? "✅" : "⚪"} {rooms.length > 0 ? `${rooms.length} pomieszczeni${rooms.length === 1 ? "e" : "a"}` : "Brak pomieszczeń"}
          </div>
          <div className={`setup-summary-item ${plantnetSaved ? "ok" : "skip"}`}>
            {plantnetSaved ? "✅" : "⚪"} PlantNet API {plantnetSaved ? "skonfigurowany" : "— pominięty"}
          </div>
          <div className={`setup-summary-item ${discordSaved ? "ok" : "skip"}`}>
            {discordSaved ? "✅" : "⚪"} Discord {discordSaved ? "skonfigurowany" : "— pominięty"}
          </div>
        </div>
        <button className="btn btn-primary setup-next" onClick={finish}>
          Przejdź do aplikacji 🌿
        </button>
      </div>
    </div>
  );
}
