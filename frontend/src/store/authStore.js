import { create } from "zustand";
import { authApi } from "../api/client";

const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  initialize: async () => {
    const token = localStorage.getItem("access_token");
    if (!token) { set({ isLoading: false, isAuthenticated: false }); return; }
    try {
      const { data } = await authApi.me();
      set({ user: data, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.clear();
      set({ isLoading: false, isAuthenticated: false });
    }
  },

  login: async (email, password) => {
    const { data } = await authApi.login({ email, password });
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    const profile = await authApi.me();
    set({ user: profile.data, isAuthenticated: true });
  },

  register: async (formData) => {
    const { data } = await authApi.register(formData);
    return data;
  },

  logout: async () => {
    try { await authApi.logout(); } catch {}
    localStorage.clear();
    set({ user: null, isAuthenticated: false });
  },
}));

export default useAuthStore;
