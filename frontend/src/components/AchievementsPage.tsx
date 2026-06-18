import { useEffect, useState } from "react";
import { api } from "../api/plants";
import type { Achievement } from "../types/plant";

export default function AchievementsPage() {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAchievements()
      .then((data) => setAchievements(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const unlocked = achievements.filter((a) => a.unlocked);
  const locked = achievements.filter((a) => !a.unlocked);

  if (loading) return <div className="achievements-loading">Ładowanie...</div>;

  return (
    <div className="achievements-page">
      <h1 className="achievements-title">Osiągnięcia</h1>
      <p className="achievements-subtitle">
        {unlocked.length} / {achievements.length} odblokowanych
      </p>

      <div className="achievements-progress-bar">
        <div
          className="achievements-progress-fill"
          style={{ width: `${achievements.length ? (unlocked.length / achievements.length) * 100 : 0}%` }}
        />
      </div>

      {unlocked.length > 0 && (
        <section className="achievements-section">
          <h2 className="achievements-section-title">✅ Odblokowane</h2>
          <div className="achievements-grid">
            {unlocked.map((a) => (
              <AchievementCard key={a.key} achievement={a} />
            ))}
          </div>
        </section>
      )}

      <section className="achievements-section">
        <h2 className="achievements-section-title">🔒 Do zdobycia</h2>
        <div className="achievements-grid">
          {locked.map((a) => (
            <AchievementCard key={a.key} achievement={a} />
          ))}
        </div>
      </section>
    </div>
  );
}

function AchievementCard({ achievement: a }: { achievement: Achievement }) {
  return (
    <div className={`achievement-card ${a.unlocked ? "achievement-card--unlocked" : "achievement-card--locked"}`}>
      <div className="achievement-icon">{a.icon}</div>
      <div className="achievement-name">{a.name}</div>
      {a.unlocked && a.unlocked_at && (
        <div className="achievement-date">
          {new Date(a.unlocked_at).toLocaleDateString("pl-PL")}
        </div>
      )}
    </div>
  );
}
