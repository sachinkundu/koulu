/**
 * Authentication context for managing user auth state.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { clearTokens, getAccessToken, getRefreshToken } from '@/lib/api-client';
import * as authApi from '../api/auth';
import * as userApi from '../api/user';
import type { LoginRequest, RegisterRequest, User } from '../types';

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps): JSX.Element {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null;

  // Load user on mount if we have tokens
  useEffect(() => {
    const loadUser = async (): Promise<void> => {
      const accessToken = getAccessToken();
      const refreshToken = getRefreshToken();

      if (accessToken === null && refreshToken === null) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await userApi.getCurrentUser();
        setUser(currentUser);
      } catch {
        // Token invalid, clear it
        clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    void loadUser();
  }, []);

  const login = useCallback(async (data: LoginRequest): Promise<void> => {
    await authApi.login(data);
    const currentUser = await userApi.getCurrentUser();
    setUser(currentUser);
  }, []);

  const register = useCallback(async (data: RegisterRequest): Promise<void> => {
    await authApi.register(data);
    // User is not logged in after registration, needs to verify email
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    await authApi.logout();
    setUser(null);
  }, []);

  const refreshUser = useCallback(async (): Promise<void> => {
    try {
      const currentUser = await userApi.getCurrentUser();
      setUser(currentUser);
    } catch {
      clearTokens();
      setUser(null);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isAuthenticated, isLoading, login, register, logout, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
