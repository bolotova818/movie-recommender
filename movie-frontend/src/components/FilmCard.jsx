// карточка фильма в списке
export default function FilmCard({ film, selected = false, onToggle, onDetails }) {
const actors = Array.isArray(film.actors) ? film.actors : [];
const firstActors = actors.slice(0, 3); // только первые три


return (
<div
className={`card ${selected ? "card--selected" : ""}`}
onClick={onToggle}
title={selected ? "Убрать из выбранных" : "Добавить к выбранным"}
>
{selected && <span className="card__check">✓</span>}


<div className="card__body">
<h3 className="card__title">{film.title}</h3>


<div className="meta">
{film.year && <span>{film.year}</span>}
{film.rating && <span>★ {Number(film.rating).toFixed(1)}</span>}
{film.director && <span>{film.director}</span>}
</div>


{film.description && <p className="desc">{film.description}</p>}


{firstActors.length > 0 && (
<div className="chips">
{firstActors.map((a, i) => (
<span className="chip" key={i}>{a}</span>
))}
</div>
)}


<div className="card__footer">
<button
className="link"
onClick={(e) => {
e.stopPropagation(); // чтобы не сработал onToggle
onDetails?.();
}}
>
Подробнее
</button>
</div>
</div>
</div>
);
}