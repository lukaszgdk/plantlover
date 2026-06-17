import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/plants";
import type { IdentifyNewResponse, Room, SunlightLevel } from "../types/plant";

type Step = "capture" | "result" | "form";

export function AddPlantForm() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  // Capture step
  const [images, setImages] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [identifying, setIdentifying] = useState(false);
  const [captureError, setCaptureError] = useState<string | null>(null);

  // Result + form step
  const [step, setStep] = useState<Step>("capture");
  const [result, setResult] = useState<IdentifyNewResponse | null>(null);
  const [showAlternatives, setShowAlternatives] = useState(false);

  // Form fields
  const [name, setName] = useState("");
  const [species, setSpecies] = useState("");
  const [commonName, setCommonName] = useState("");
  const [wateringDays, setWateringDays] = useState<number>(7);
  const [sunlight, setSunlight] = useState<SunlightLevel | "">("");
  const [notes, setNotes] = useState("");
  const [roomId, setRoomId] = useState<string>("");
  const [rooms, setRooms] = useState<Room[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    api.listRooms().then(setRooms).catch(() => {});
  }, []);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (!files.length) return;
    const combined = [...images, ...files].slice(0, 5);
    setImages(combined);
    setPreviews(combined.map((f) => URL.createObjectURL(f)));
    setCaptureError(null);
  }

  function removeImage(idx: number) {
    const next = images.filter((_, i) => i !== idx);
    setImages(next);
    setPreviews(next.map((f) => URL.createObjectURL(f)));
  }

  async function handleIdentify() {
    if (!images.length) {
      setCaptureError("Add at least one photo.");
      return;
    }
    setIdentifying(true);
    setCaptureError(null);
    try {
      const res = await api.identifyNew(images);
      setResult(res);
      setSpecies(res.top.species);
      setCommonName(res.top.common_name ?? "");
      setName(res.top.common_name || res.top.species);
      setStep("result");
    } catch (e) {
      setCaptureError((e as Error).message);
    } finally {
      setIdentifying(false);
    }
  }

  function handleReset() {
    setImages([]);
    setPreviews([]);
    setResult(null);
    setStep("capture");
    setCaptureError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  function applyAlternative(idx: number) {
    if (!result) return;
    const alt = result.alternatives[idx];
    setSpecies(alt.species);
    setCommonName(alt.common_name ?? "");
    setName(alt.common_name || alt.species);
    setShowAlternatives(false);
  }

  async function handleSave() {
    if (!name.trim()) {
      setFormError("Plant name is required.");
      return;
    }
    setSubmitting(true);
    setFormError(null);
    try {
      const plant = await api.createWithPhoto(
        {
          name: name.trim(),
          species: species || undefined,
          common_name: commonName || undefined,
          watering_interval_days: wateringDays > 0 ? wateringDays : undefined,
          sunlight: sunlight || undefined,
          notes: notes || undefined,
          room_id: roomId || undefined,
        },
        images[0],
      );
      navigate(`/plants/${plant.id}`);
    } catch (e) {
      setFormError((e as Error).message);
      setSubmitting(false);
    }
  }

  // ── Step 1: Capture ────────────────────────────────────────────────────────
  if (step === "capture") {
    return (
      <div className="form-page">
        <div className="page-header">
          <h1>Add Plant</h1>
          <button className="btn btn-secondary" onClick={() => navigate(-1)}>
            Cancel
          </button>
        </div>

        <div className="identify-capture">
          <p className="identify-hint">
            Take up to 5 photos from different angles for best results.
          </p>

          {previews.length > 0 && (
            <div className="capture-thumbnails">
              {previews.map((src, i) => (
                <div key={i} className="capture-thumb-wrap">
                  <img src={src} alt={`Photo ${i + 1}`} className="capture-thumb" />
                  <button
                    className="capture-thumb-remove"
                    onClick={() => removeImage(i)}
                    aria-label="Remove"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {images.length < 5 && (
            <label className="btn btn-secondary photo-capture-trigger">
              📷 {images.length === 0 ? "Take photo" : "Add another photo"}
              <input
                ref={inputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleFileChange}
                style={{ display: "none" }}
              />
            </label>
          )}

          {captureError && <p className="status error">{captureError}</p>}

          <button
            className="btn btn-primary"
            onClick={handleIdentify}
            disabled={identifying || images.length === 0}
            style={{ marginTop: "1rem" }}
          >
            {identifying ? "Identifying…" : "🔍 Identify plant"}
          </button>
        </div>
      </div>
    );
  }

  // ── Step 2: Result + Form ──────────────────────────────────────────────────
  return (
    <div className="form-page">
      <div className="page-header">
        <h1>Save Plant</h1>
        <button className="btn btn-secondary" onClick={handleReset}>
          ← Try again
        </button>
      </div>

      {result && (
        <div className="identify-result-card">
          {previews[0] && (
            <img src={previews[0]} alt="Plant photo" className="identify-result-photo" />
          )}
          <div className="identify-result-info">
            <p className="identify-species">{result.top.species}</p>
            {result.top.common_name && (
              <p className="identify-common">{result.top.common_name}</p>
            )}
            <p className="identify-score">
              Confidence: {Math.round(result.top.score * 100)}%
              {result.top.score < 0.3 && (
                <span className="identify-warning"> ⚠️ Low — verify manually</span>
              )}
            </p>

            {result.alternatives.length > 0 && (
              <div>
                <button
                  className="btn btn-secondary"
                  style={{ padding: "0.25rem 0.75rem", fontSize: "0.85rem" }}
                  onClick={() => setShowAlternatives((v) => !v)}
                >
                  {showAlternatives ? "Hide alternatives" : "Show alternatives"}
                </button>
                {showAlternatives && (
                  <ul className="identify-alternatives">
                    {result.alternatives.map((alt, i) => (
                      <li key={i}>
                        <button
                          className="identify-alt-btn"
                          onClick={() => applyAlternative(i)}
                        >
                          <span className="identify-alt-species">{alt.species}</span>
                          {alt.common_name && (
                            <span className="identify-alt-common"> ({alt.common_name})</span>
                          )}
                          <span className="identify-alt-score">
                            {" "}{Math.round(alt.score * 100)}%
                          </span>
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      <form
        className="plant-form"
        onSubmit={(e) => {
          e.preventDefault();
          handleSave();
        }}
      >
        <label>
          Name <span className="required">*</span>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Kitchen Monstera"
            autoFocus
          />
        </label>

        <label>
          Species (from identification)
          <input
            value={species}
            onChange={(e) => setSpecies(e.target.value)}
            placeholder="e.g. Monstera deliciosa"
          />
        </label>

        <label>
          Common name
          <input
            value={commonName}
            onChange={(e) => setCommonName(e.target.value)}
          />
        </label>

        <label>
          Room
          <select value={roomId} onChange={(e) => setRoomId(e.target.value)}>
            <option value="">— no room —</option>
            {rooms.map((r) => (
              <option key={r.id} value={r.id}>
                {r.icon} {r.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Watering interval (days)
          <input
            type="number"
            min={1}
            value={wateringDays}
            onChange={(e) => setWateringDays(Number(e.target.value))}
          />
        </label>

        <label>
          Sunlight
          <select
            value={sunlight}
            onChange={(e) => setSunlight(e.target.value as SunlightLevel | "")}
          >
            <option value="">— select —</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>

        <label>
          Notes
          <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </label>

        {formError && <p className="status error">{formError}</p>}

        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? "Saving…" : "💾 Zapisz roślinę"}
        </button>
      </form>
    </div>
  );
}
