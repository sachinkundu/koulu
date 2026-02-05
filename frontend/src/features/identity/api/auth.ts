/**
 * Authentication API functions.
 */

import { apiClient, clearTokens, setTokens } from '@/lib/api-client';
import type {
  AuthTokens,
  ForgotPasswordRequest,
  LoginRequest,
  MessageResponse,
  RegisterRequest,
  ResetPasswordRequest,
  VerifyEmailRequest,
} from '../types';

/**
 * Register a new user.
 */
export async function register(data: RegisterRequest): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/register', data);
  return response.data;
}

/**
 * Verify email with token.
 */
export async function verifyEmail(data: VerifyEmailRequest): Promise<AuthTokens> {
  const response = await apiClient.post<AuthTokens>('/auth/verify', data);
  const tokens = response.data;
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}

/**
 * Resend verification email.
 */
export async function resendVerification(email: string): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/verify/resend', { email });
  return response.data;
}

/**
 * Log in with email and password.
 */
export async function login(data: LoginRequest): Promise<AuthTokens> {
  const response = await apiClient.post<AuthTokens>('/auth/login', data);
  const tokens = response.data;
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}

/**
 * Log out (invalidate refresh token).
 */
export async function logout(): Promise<void> {
  const refreshToken = localStorage.getItem('koulu_refresh_token');
  if (refreshToken !== null) {
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    } catch {
      // Ignore errors, still clear tokens locally
    }
  }
  clearTokens();
}

/**
 * Request password reset email.
 */
export async function forgotPassword(data: ForgotPasswordRequest): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/password/forgot', data);
  return response.data;
}

/**
 * Reset password with token.
 */
export async function resetPassword(data: ResetPasswordRequest): Promise<MessageResponse> {
  const response = await apiClient.post<MessageResponse>('/auth/password/reset', data);
  return response.data;
}
