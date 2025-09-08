import { useEffect, useState } from "react";
import { getRandomFilms, getRecommendations } from "./services/api";
import FilmCard from "./components/FilmCard";
import DetailsModal from "./components/DetailsModal";
import RecItem from "./components/RecItem";
import "./App.css";

const MAX_SELECTED = 10; // удобно менять лимит в одном месте

function App() {
  const [films, setFilms] = useState([]);
  const [selected, setSelected] = useState([]);
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [active, setActive] = useState(null);

  useEffect(() => {
    loadRandom();
  }, []);

  async function loadRandom() {
    setError("");
    setLoading(true);
    try {
      const data = await getRandomFilms(30);
      // подстраховка на случай кривого ответа API
      setFilms(Array.isArray(data) ? data : []);
      setSelected([]);
      setRecs([]);
      setActive(null);
    } catch (e) {
      console.error(e);
      setError("Не получилось загрузить фильмы.");
    } finally {
      setLoading(false);
    }
  }

  function toggleSelect(title) {
    setError("");
    setRecs([]); // при новом выборе сбрасываем рекомендации

    setSelected((prev) => {
      if (prev.includes(title)) return prev.filter((t) => t !== title);
      if (prev.length >= MAX_SELECTED) {
        setError(`Можно выбрать максимум ${MAX_SELECTED} фильмов.`);
        return prev;
      }
      return [...prev, title];
    });
  }

  async function fetchRecs() {
    if (selected.length === 0) {
      setError("Сначала выбери хотя бы один фильм.");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const data = await getRecommendations(selected, 10);
      setRecs(Array.isArray(data) ? data : []);

      // небольшая визуальная подсветка сайдбара
      requestAnimationFrame(() => {
        const aside = document.querySelector(".aside");
        if (aside) {
          aside.classList.add("aside--pulse");
          setTimeout(() => aside.classList.remove("aside--pulse"), 900);
        }
      });
    } catch (e) {
      console.error(e);
      setRecs([]);
      setError("Не получилось получить рекомендации.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>Movie Recommender</h1>
      </header>

      <div className="toolbar">
        <button className="btn" onClick={loadRandom} disabled={loading}>
          Показать случайные фильмы
        </button>

        <div className="counter">
          Выбрано: <b>{selected.length}</b>/{MAX_SELECTED}
          {selected.length > 0 && (
            <button
              className="link"
              onClick={() => {
                setSelected([]);
                setRecs([]);
                setError("");
              }}
            >
              очистить
            </button>
          )}
        </div>

        <button
          className="btn primary"
          onClick={fetchRecs}
          disabled={loading || selected.length === 0}
        >
          Получить рекомендации
        </button>
      </div>

      {error && <div className="alert">{error}</div>}
      {loading && <div className="loading">Загрузка…</div>}

      <div className="layout">
        <main className="main">
          <h2 className="sectionTitle">Случайные фильмы</h2>

          <div className="grid">
            {films.map((f) => (
              <FilmCard
                key={f.title}
                film={f}
                selected={selected.includes(f.title)}
                onToggle={() => toggleSelect(f.title)}
                onDetails={() => setActive(f)}
              />
            ))}
          </div>
        </main>

        <aside className="aside">
          <div className="aside__header">
            <h3>Рекомендации</h3>
            {recs.length > 0 && <span className="badge">{recs.length}</span>}
          </div>

          <div className="aside__hint">
            {recs.length === 0
              ? "Выбери до 10 фильмов и нажми «Получить рекомендации»."
              : "Клик по карточке — откроет подробности."}
          </div>

          <div className="aside__list">
            {recs.map((f, i) => (
              <RecItem
                key={f.title || i}
                film={f}
                onDetails={() => setActive(f)}
              />
            ))}
          </div>
        </aside>
      </div>

      <DetailsModal
        film={active}
        selected={!!active && selected.includes(active.title)}
        onClose={() => setActive(null)}
        onToggleSelect={toggleSelect}
      />
    </div>
  );
}

export default App;