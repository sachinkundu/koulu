/**
 * Axios API client with authentication interceptors.
 */

import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';

// Token storage keys
const ACCESS_TOKEN_KEY = 'koulu_access_token';
const REFRESH_TOKEN_KEY = 'koulu_refresh_token';

/**
 * Get stored access token.
 */
export function getAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Get stored refresh token.
 */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store authentication tokens.
 */
export function setTokens(accessToken: string, refreshToken: string): void {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

/**
 * Clear stored tokens.
 */
export function clearTokens(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Create axios instance with base configuration.
 */
function createApiClient(): AxiosInstance {
  const client: AxiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: 10000,
  });

  // Request interceptor - add auth token
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = getAccessToken();
      if (token !== null && config.headers !== undefined) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error: AxiosError) => Promise.reject(error)
  );

  // Response interceptor - handle token refresh
  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config;

      // If 401 and we have a refresh token, try to refresh
      const hasRetried = (originalRequest as { _retry?: boolean } | undefined)?._retry === true;
      if (
        error.response?.status === 401 &&
        originalRequest !== undefined &&
        !hasRetried
      ) {
        const refreshToken = getRefreshToken();

        if (refreshToken !== null && refreshToken !== '') {
          (originalRequest as { _retry?: boolean })._retry = true;

          try {
            const response = await axios.post<{
              access_token: string;
              refresh_token: string;
            }>(`${API_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token } = response.data;
            setTokens(access_token, refresh_token);

            // Retry original request with new token
            if (originalRequest.headers !== undefined) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
            }
            return client(originalRequest);
          } catch {
            // Refresh failed, clear tokens and redirect to login
            clearTokens();
            window.location.href = '/login';
            return Promise.reject(error);
          }
        }
      }

      return Promise.reject(error);
    }
  );

  return client;
}

export const apiClient = createApiClient();
