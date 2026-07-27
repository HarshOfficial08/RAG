import { createContext } from "react";
import { jwtDecode } from "jwt-decode";

export interface TokenClaims {
  sub: string;
  tenant_id: string;
  tenant_name?: string;
  exp: number;
}

export interface AuthState {
  userId: string | null;
  tenantId: string | null;
  tenantName: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
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
