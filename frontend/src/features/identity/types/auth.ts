/**
 * Authentication types for the Identity context.
 */

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_at: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface VerifyEmailRequest {
  token: string;
}

export interface ResendVerificationRequest {
  email: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

export interface CompleteProfileRequest {
  display_name: string;
  avatar_url?: string | null;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface LogoutRequest {
  refresh_token: string;
}

export interface MessageResponse {
  message: string;
}

export interface ErrorResponse {
  code: string;
  message: string;
}

export interface ApiError {
  response?: {
    data?: ErrorResponse;
    status?: number;
  };
}
