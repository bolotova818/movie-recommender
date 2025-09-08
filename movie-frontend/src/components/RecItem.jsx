// карточка в блоке рекомендаций (правая колонка)
export default function RecItem({ film, onDetails }) {
// описание в одну строку, чтобы не было переносов
const desc = String(film.description || "")
.replace(/\s*\n\s*/g, " ")
.trim();


return (
<div className="recItem" onClick={onDetails} title="Открыть подробности">
<div className="recItem__body">
<div className="recItem__title">{film.title}</div>


<div className="recItem__meta">
{film.year && <span>{film.year}</span>}
{film.rating && <span>★ {Number(film.rating).toFixed(1)}</span>}
{film.director && <span>{film.director}</span>}
</div>


{desc && <p className="recItem__desc">{desc}</p>}
</div>
</div>
);
}