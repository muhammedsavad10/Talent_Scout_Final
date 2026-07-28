import { create } from 'zustand';
import type { AuthState, User } from '../types/auth';
import { loginApi, fetchCurrentUserApi, refreshTokenApi, logoutApi } from '../api/authApi';

const ACCESS_TOKEN_KEY = 'talentscout_access_token';
const REFRESH_TOKEN_KEY = 'talentscout_refresh_token';
const USER_KEY = 'talentscout_user_profile';

const getInitialTokens = () => {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  const userJson = localStorage.getItem(USER_KEY);
  let user: User | null = null;
  if (userJson) {
    try {
      user = JSON.parse(userJson);
    } catch {
      user = null;
    }
  }
  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated: Boolean(accessToken && user),
  };
};

export const useAuthStore = create<AuthState>((set, get) => {
  const initial = getInitialTokens();

  return {
    user: initial.user,
    accessToken: initial.accessToken,
    refreshToken: initial.refreshToken,
    isAuthenticated: initial.isAuthenticated,
    isLoading: false, // Default to false; set true only during active async operations
    error: null,

    login: async (credentials) => {
      set({ isLoading: true, error: null });
      try {
        const response = await loginApi(credentials);
        const { access_token, refresh_token, user } = response;

        localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));

        set({
          user,
          accessToken: access_token,
          refreshToken: refresh_token,
          isAuthenticated: true,
          error: null,
        });
      } catch (err: any) {
        const errorMessage =
          err?.response?.data?.detail ||
          err?.message ||
          'Invalid email or password. Please try again.';

        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        localStorage.removeItem(USER_KEY);

        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: errorMessage,
        });
        throw new Error(errorMessage);
      } finally {
        set({ isLoading: false });
      }
    },

    logout: async () => {
      set({ isLoading: true });
      const currentRefresh = get().refreshToken || localStorage.getItem(REFRESH_TOKEN_KEY);
      try {
        if (currentRefresh) {
          await logoutApi(currentRefresh);
        }
      } catch {
        // Silently catch network errors on logout
      } finally {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        localStorage.removeItem(USER_KEY);

        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      }
    },

    refreshSession: async () => {
      const currentRefresh = get().refreshToken || localStorage.getItem(REFRESH_TOKEN_KEY);
      if (!currentRefresh) {
        await get().logout();
        return false;
      }

      try {
        const response = await refreshTokenApi(currentRefresh);
        const { access_token, refresh_token, user } = response;

        localStorage.setItem(ACCESS_TOKEN_KEY, access_token);
        localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));

        set({
          user,
          accessToken: access_token,
          refreshToken: refresh_token,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
        return true;
      } catch {
        await get().logout();
        return false;
      }
    },

    checkAuth: async () => {
      const currentAccess = get().accessToken || localStorage.getItem(ACCESS_TOKEN_KEY);
      if (!currentAccess) {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
        return;
      }

      set({ isLoading: true });
      try {
        const user = await fetchCurrentUserApi(currentAccess);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
        set({
          user,
          isAuthenticated: true,
          error: null,
        });
      } catch {
        const success = await get().refreshSession();
        if (!success) {
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
          });
        }
      } finally {
        set({ isLoading: false });
      }
    },

    clearError: () => set({ error: null }),
  };
});
