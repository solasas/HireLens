import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * The backend's error handler always returns { detail: "message" } for
 * AppError subclasses (see app.main.handle_app_error). Every page in
 * this app reads errors through this helper instead of reaching into
 * error.response.data itself, so that shape lives in exactly one place.
 */
export function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }
  if (error?.message) {
    return error.message;
  }
  return "Something went wrong. Please try again.";
}
