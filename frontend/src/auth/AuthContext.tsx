import { useMemo, useState, type ReactNode } from "react";
import { setAuthToken } from "../api/client";
import { login as loginRequest } from "../api/auth";
import { AuthContext, decodeToken, STORAGE_KEY, type AuthState, type TokenClaims } from "./context";

function loadStoredClaims(): TokenClaims | null {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) return null;
  const decoded = decodeToken(stored);
  if (decoded && decoded.exp * 1000 > Date.now()) {
    setAuthToken(stored);
    return decoded;
  }
  localStorage.removeItem(STORAGE_KEY);
  return null;
}

export function AuthProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [claims, setClaims] = useState<TokenClaims | null>(loadStoredClaims);

  const value = useMemo<AuthState>(
    () => ({
      userId: claims?.sub ?? null,
      tenantId: claims?.tenant_id ?? null,
      tenantName: claims?.tenant_name ?? null,
      isAuthenticated: claims !== null,
      login: async (email: string, password: string) => {
        const { token } = await loginRequest(email, password);
        const decoded = decodeToken(token);
        if (!decoded) throw new Error("Received an invalid token from the server");
        localStorage.setItem(STORAGE_KEY, token);
        setAuthToken(token);
        setClaims(decoded);
      },
      logout: () => {
        localStorage.removeItem(STORAGE_KEY);
        setAuthToken(null);
        setClaims(null);
      },
    }),
    [claims],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
