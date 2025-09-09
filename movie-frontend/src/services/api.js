// src/services/api.js
import axios from "axios";

// Берём базовый URL из env, убираем завершающий слэш
const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");

if (!API_BASE) {
  console.warn(
    "VITE_API_BASE_URL не задан. Создай .env.local и пропиши адрес API."
  );
}

// Единый клиент
const http = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});


async function getRandomFilmsInternal(limit) {
  try {
    const res = await http.get("/films/random", { params: { limit } });
    return res.data;
  } catch (e) {
    if (e?.response?.status === 404) {
      const res = await http.get("/random_films", { params: { limit } });
      return res.data;
    }
    throw e;
  }
}

// Загрузка случайных фильмов
export async function getRandomFilms(limit = 30) {
  try {
    const data = await getRandomFilmsInternal(limit);
    return Array.isArray(data) ? data : [];
  } catch (e) {
    console.error("Ошибка при загрузке фильмов:", e);
    return [];
  }
}

// Рекомендации на основе выбранных фильмов
export async function getRecommendations(likedTitles, topN = 10) {
  try {
    const res = await http.post("/recommend", {
      liked_titles: likedTitles,
      top_n: topN,
    });
    return res.data?.recommendations || [];
  } catch (e) {
    console.error("Ошибка при получении рекомендаций:", e);
    return [];
  }
}

// Поможет быстро проверить, куда стучится фронт
export const __API_BASE__ = API_BASE;
