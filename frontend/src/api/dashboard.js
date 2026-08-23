import { apiClient } from "./client";

export async function getDashboardStats() {
  const response = await apiClient.get("/dashboard");
  return response.data;
}
