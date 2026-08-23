import { apiClient } from "./client";

export async function getEvaluation(evaluationId) {
  const response = await apiClient.get(`/evaluations/${evaluationId}`);
  return response.data;
}
