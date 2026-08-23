import { apiClient } from "./client";

export async function listJobs() {
  const response = await apiClient.get("/jobs");
  return response.data;
}

export async function getJob(jobId) {
  const response = await apiClient.get(`/jobs/${jobId}`);
  return response.data;
}

export async function createJob(text) {
  const response = await apiClient.post("/jobs", { text });
  return response.data;
}

export async function evaluateCandidates(jobId, files, onUploadProgress) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  const response = await apiClient.post(`/jobs/${jobId}/candidates`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress,
  });
  return response.data;
}

export async function getCandidateRanking(jobId, { page = 1, pageSize = 20 } = {}) {
  const response = await apiClient.get(`/jobs/${jobId}/candidates`, {
    params: { page, page_size: pageSize },
  });
  return response.data;
}
