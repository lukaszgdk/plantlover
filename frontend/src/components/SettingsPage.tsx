import { useEffect, useState } from "react";
import { api } from "../api/plants";
import type { AppConfig, Room } from "../types/plant";

const ROOM_ICONS = ["🛋️", "🛏️", "🚿", "🍳", "🪟", "🌿", "🏡", "📚", "🪴", "💼"];

export function SettingsPage() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);

  const [plantnetKey, setPlantnetKey] = useState("");
  const [plantnetMsg, setPlantnetMsg] = useState<string | null>(null);

  const [discordToken, setDiscordToken] = useState("");
  const [discordChannel, setDiscordChannel] = useState("");
  const [discordMsg, setDiscordMsg] = useState<string | null>(null);

  const [roomName, setRoomName] = useState("");
  const [roomIcon, setRoomIcon] = useState("🌿");
  const [roomMsg, setRoomMsg] = useState<string | null>(null);

  useEffect(() => {
    api.getConfig().then((cfg) => {
      setConfig(cfg);
      if (cfg.discord_channel_id) setDiscordChannel(cfg.discord_channel_id);
    });
    api.listRooms().then(setRooms);
  }, []);

  async function savePlantnet() {
    if (!plantnetKey.trim()) return;
    try {
      await api.saveConfig({ plantnet_api_key: plantnetKey.trim() });
      setPlantnetMsg("✅ Zapisano");
      setPlantnetKey("");
      api.getConfig().then(setConfig);
    } catch {
      setPlantnetMsg("❌ Błąd zapisu");
    }
  }

  async function saveDiscord() {
    try {
      await api.saveConfig({
        discord_bot_token: discordToken.trim() || undefined,
        discord_channel_id: discordChannel.trim() || undefined,
      } as Parameters<typeof api.saveConfig>[0]);
      setDiscordMsg("✅ Zapisano. Bot zostanie zrestartowany.");
      setDiscordToken("");
      api.getConfig().then(setConfig);
    } catch {
      setDiscordMsg("❌ Błąd zapisu");
    }
  }

  async function addRoom() {
    if (!roomName.trim()) return;
    try {
      const r = await api.createRoom({ name: roomName.trim(), icon: roomIcon });
      setRooms((prev) => [...prev, r]);
      setRoomName("");
      setRoomMsg(null);
    } catch {
      setRoomMsg("❌ Błąd dodawania");
    }
  }

  async function deleteRoom(id: string) {
    try {
      await api.deleteRoom(id);
      setRooms((prev) => prev.filter((r) => r.id !== id));
    } catch {
      setRoomMsg("❌ Nie można usunąć — sprawdź czy pokój nie ma przypisanych roślin");
    }
  }

  return (
    <div className="settings-page">
      <h1>⚙️ Ustawienia</h1>

      {/* Rooms */}
      <section className="settings-section">
        <h2>🏠 Pomieszczenia</h2>
        <ul className="setup-room-list">
          {rooms.map((r) => (
            <li key={r.id} className="setup-room-item">
              <span>{r.icon} {r.name}</span>
              <button className="btn-icon-delete" onClick={() => deleteRoom(r.id)}>×</button>
            </li>
          ))}
        </ul>
        <div className="setup-icon-picker" style={{ marginTop: "0.75rem" }}>
          {ROOM_ICONS.map((icon) => (
            <button key={icon} className={`icon-btn ${roomIcon === icon ? "selected" : ""}`}
              onClick={() => setRoomIcon(icon)} type="button">{icon}</button>
          ))}
        </div>
        <div className="setup-room-input-row">
          <span className="setup-selected-icon">{roomIcon}</span>
          <input value={roomName} onChange={(e) => setRoomName(e.target.value)}
            placeholder="Nazwa pomieszczenia" onKeyDown={(e) => e.key === "Enter" && addRoom()} />
          <button className="btn btn-primary" onClick={addRoom}>+ Dodaj</button>
        </div>
        {roomMsg && <p className="status">{roomMsg}</p>}
      </section>

      {/* PlantNet */}
      <section className="settings-section">
        <h2>📷 PlantNet API</h2>
        <p className="settings-status">
          Status: {config?.plantnet_api_key_set ? "✅ skonfigurowany" : "⚠️ brak klucza"}
        </p>
        <div className="setup-input-group">
          <input type="password" value={plantnetKey}
            onChange={(e) => setPlantnetKey(e.target.value)}
            placeholder="Nowy klucz API PlantNet"
            onKeyDown={(e) => e.key === "Enter" && savePlantnet()} />
          <button className="btn btn-primary" onClick={savePlantnet}>Zapisz</button>
        </div>
        {plantnetMsg && <p className="status">{plantnetMsg}</p>}
      </section>

      {/* Discord */}
      <section className="settings-section">
        <h2>💬 Discord Bot</h2>
        <p className="settings-status">
          Status: {config?.discord_bot_token_set ? "✅ skonfigurowany" : "⚠️ brak tokena"}
          {config?.discord_channel_id && ` — kanał ${config.discord_channel_id}`}
        </p>
        <div className="setup-input-group">
          <label>
            Token bota (zostaw puste żeby nie zmieniać)
            <input type="password" value={discordToken}
              onChange={(e) => setDiscordToken(e.target.value)}
              placeholder="Bot token" />
          </label>
          <label>
            ID kanału
            <input value={discordChannel}
              onChange={(e) => setDiscordChannel(e.target.value)}
              placeholder="np. 1516900842588995704" />
          </label>
          <button className="btn btn-primary" onClick={saveDiscord}>Zapisz</button>
        </div>
        {discordMsg && <p className="status">{discordMsg}</p>}
      </section>
    </div>
  );
}
