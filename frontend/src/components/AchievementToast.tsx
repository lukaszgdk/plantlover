import { useEffect, useState } from "react";
import type { Achievement } from "../types/plant";

interface Props {
  achievements: Achievement[];
  keys: string[];
  onDone: () => void;
}

export function AchievementToast({ achievements, keys, onDone }: Props) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => {
      setVisible(false);
      setTimeout(onDone, 400);
    }, 4000);
    return () => clearTimeout(t);
  }, [onDone]);

  const unlocked = achievements.filter((a) => keys.includes(a.key));
  if (!unlocked.length) return null;

  return (
    <div className={`achievement-toast ${visible ? "achievement-toast--visible" : "achievement-toast--hidden"}`}>
      {unlocked.map((a) => (
        <div key={a.key} className="achievement-toast-item">
          <span className="achievement-toast-icon">{a.icon}</span>
          <div className="achievement-toast-text">
            <div className="achievement-toast-headline">🏅 Nowe osiągnięcie!</div>
            <div className="achievement-toast-name">{a.name}</div>
            <div className="achievement-toast-desc">{a.description}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
