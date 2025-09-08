import axios from "axios";

// адрес сервера, можно вынести в .env
const API_URL = "http://127.0.0.1:8000";

// загрузка случайных фильмов
export async function getRandomFilms(limit = 30) {
  try {
    const res = await axios.get(`${API_URL}/films/random`, {
      params: { limit },
    });
    return Array.isArray(res.data) ? res.data : [];
  } catch (e) {
    console.error("Ошибка при загрузке фильмов:", e);
    return [];
  }
}

// рекомендации на основе выбранных фильмов
export async function getRecommendations(likedTitles, topN = 10) {
  try {
    const res = await axios.post(`${API_URL}/recommend`, {
      liked_titles: likedTitles,
      top_n: topN,
    });
    // если бэкенд вернул не тот формат — вернём пустой массив
    return res.data?.recommendations || [];
  } catch (e) {
    console.error("Ошибка при получении рекомендаций:", e);
    return [];
  }
}