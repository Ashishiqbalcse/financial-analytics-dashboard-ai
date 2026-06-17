
import axios from "axios";

const API_BASE_URL =
  "http://127.0.0.1:7777/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,

  headers: {
    "Content-Type":
      "application/json",
  },

  timeout: 30000,
});

api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem(
        "token"
      );

    if (
      token &&
      config.headers
    ) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },

  (error) => {
    return Promise.reject(
      error
    );
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },

  (error) => {
    console.error(
      "API Error:",
      error
    );

    return Promise.reject(
      error
    );
  }
);

export default api;
