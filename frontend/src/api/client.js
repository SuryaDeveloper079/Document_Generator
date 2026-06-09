import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
});

export const projectsApi = {
  list: () => api.get("/projects"),
  create: (data) => api.post("/projects", data),
  get: (id) => api.get(`/projects/${id}`),
  delete: (id) => api.delete(`/projects/${id}`),
};

export const documentsApi = {
  list: (projectId) => api.get(`/projects/${projectId}/documents`),
  create: (projectId, data) => api.post(`/projects/${projectId}/documents`, data),
  get: (projectId, docId) => api.get(`/projects/${projectId}/documents/${docId}`),
  taskStatus: (projectId, docId) => api.get(`/projects/${projectId}/documents/${docId}/task-status`),
  delete: (projectId, docId) => api.delete(`/projects/${projectId}/documents/${docId}`),
};

export default api;
