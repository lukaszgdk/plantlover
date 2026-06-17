import { useRef, useState } from "react";
import { api } from "../api/plants";
import type { IdentifyResponse } from "../types/plant";

interface Props {
  plantId: string;
  onIdentified?: (result: IdentifyResponse) => void;
}

export function PhotoCapture({ plantId, onIdentified }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IdentifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setResult(null);
    setError(null);
    const url = URL.createObjectURL(file);
    setPreview(url);
  }

  async function handleIdentify() {
    if (!selectedFile) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.identifyImage(plantId, selectedFile);
      setResult(res);
      onIdentified?.(res);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setPreview(null);
    setSelectedFile(null);
    setResult(null);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div className="photo-capture">
      {!preview ? (
        <label className="btn btn-secondary photo-capture-trigger">
          📷 Identify with camera
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />
        </label>
      ) : (
        <div className="photo-capture-preview">
          <img src={preview} alt="Preview" className="capture-preview-img" />
          <div className="capture-actions">
            {!result && (
              <button
                className="btn btn-primary"
                onClick={handleIdentify}
                disabled={loading}
              >
                {loading ? "Identifying…" : "Identify plant"}
              </button>
            )}
            <button className="btn btn-secondary" onClick={handleReset}>
              Reset
            </button>
          </div>

          {error && <p className="status error">{error}</p>}

          {result && (
            <div className="identify-result">
              <p className="identify-species">{result.species}</p>
              {result.common_name && (
                <p className="identify-common">{result.common_name}</p>
              )}
              <p className="identify-score">
                Confidence: {Math.round(result.score * 100)}%
              </p>
              {result.score < 0.3 && (
                <p className="identify-warning">
                  ⚠️ Low confidence — verify manually
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
