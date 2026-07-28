import { createContext } from "react";
import { jwtDecode } from "jwt-decode";

export interface TokenClaims {
  sub: string;
  tenant_id: string;
  tenant_name?: string;
  role?: string;
  email?: string;
  name?: string;
  exp: number;
}

export interface AuthState {
  userId: string | null;
  tenantId: string | null;
  tenantName: string | null;
  role: string | null;
  email: string | null;
  name: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  // Two-step, email-verified signup: requestSignupOtp() stashes the pending
  // signup server-side and emails a 6-digit code (no account exists yet);
  // verifySignupOtp() checks the code, actually creates the account, and
  // (on success) applies the returned token exactly like login() does.
  requestSignupOtp: (
    organizationName: string,
    email: string,
    password: string,
    name: string,
  ) => Promise<void>;
  verifySignupOtp: (email: string, code: string) => Promise<void>;
  // Settings: change the current account's password (requires re-entering
  // the current one). Doesn't change the token — claims are unaffected.
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  // Settings: two-step, OTP-verified email change. requestChangeEmailOtp()
  // re-checks the current password and emails a 6-digit code to the NEW
  // address (nothing changes yet); verifyChangeEmailOtp() checks the code,
  // actually swaps the account's email server-side, and (on success)
  // applies the freshly issued token exactly like login()/verifySignupOtp() do.
  requestChangeEmailOtp: (newEmail: string, currentPassword: string) => Promise<void>;
  verifyChangeEmailOtp: (code: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthState | null>(null);

export const STORAGE_KEY = "securerag_token";

// Claims here are for display only (e.g. showing the tenant name in the top bar).
// The backend re-verifies the token signature on every request — the UI never
// makes an authorization decision based on this decoded payload.
export function decodeToken(token: string): TokenClaims | null {
  try {
    return jwtDecode<TokenClaims>(token);
  } catch {
    return null;
  }
}
