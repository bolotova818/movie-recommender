import { useMemo } from "react";


// модальное окно с подробной инфой о фильме
export default function DetailsModal({ film, selected, onClose, onToggleSelect }) {
if (!film) return null; // если фильма нет — нечего показывать


const actors = Array.isArray(film.actors) ? film.actors : [];
const countries = Array.isArray(film.country) ? film.country : [];


// приводим описание в одну строку, чтобы выглядело аккуратно
const desc = useMemo(() => {
return String(film.description || "").replace(/\s*\n\s*/g, " ").trim();
}, [film.description]);


return (
<div className="modalOverlay" onClick={onClose}>
<div className="modal" onClick={(e) => e.stopPropagation()}>
<button className="modal__close" onClick={onClose} aria-label="Закрыть">
×
</button>


<div className="modal__content">
<div className="modal__body">
<h3 className="modal__title">{film.title}</h3>


<div className="modal__meta">
{film.year && <span>{film.year}</span>}
{film.rating && <span>★ {Number(film.rating).toFixed(1)}</span>}
{film.director && <span>{film.director}</span>}
{countries.length > 0 && <span>{countries.join(", ")}</span>}
</div>


{desc && <p className="modal__desc">{desc}</p>}


{actors.length > 0 && (
<>
<div className="modal__subtitle">Актёры</div>
<div className="chips">
{actors.map((a, i) => (
<span className="chip" key={i}>{a}</span>
))}
</div>
</>
)}


<div className="modal__actions">
<button
className={`btn ${selected ? "" : "primary"}`}
onClick={() => onToggleSelect?.(film.title)}
>
{selected ? "Убрать из выбранных" : "Добавить к выбранным"}
</button>


<button className="btn" onClick={onClose}>
Закрыть
</button>
</div>
</div>
</div>
</div>
</div>
);
}