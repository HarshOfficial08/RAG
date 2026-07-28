import { useEffect, useMemo, useState, type ReactNode } from "react";
import { setAuthToken } from "../api/client";
import {
  changePassword as changePasswordRequest,
  login as loginRequest,
  requestChangeEmailOtp as requestChangeEmailOtpRequest,
  requestSignupOtp as requestSignupOtpRequest,
  verifyChangeEmailOtp as verifyChangeEmailOtpRequest,
  verifySignupOtp as verifySignupOtpRequest,
} from "../api/auth";
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

  useEffect(() => {
    // The browser can restore a full page snapshot from bfcache on back/
    // forward navigation without re-running any of this app's mount logic —
    // React's in-memory state (and the auth check RequireAuth made) would
    // otherwise stay frozen from before the navigation, which can show
    // protected content without a valid session, or show a logged-out
    // screen while still genuinely logged in. Re-derive from localStorage
    // (the actual source of truth) whenever that happens.
    function resync() {
      setClaims(loadStoredClaims());
    }

    function handlePageShow(event: PageTransitionEvent) {
      if (event.persisted) resync();
    }

    // Also keep multiple tabs consistent: logging out in one tab should be
    // reflected in others rather than leaving them showing stale auth state.
    function handleStorage(event: StorageEvent) {
      if (event.key === STORAGE_KEY) resync();
    }

    window.addEventListener("pageshow", handlePageShow);
    window.addEventListener("storage", handleStorage);
    return () => {
      window.removeEventListener("pageshow", handlePageShow);
      window.removeEventListener("storage", handleStorage);
    };
  }, []);

  const value = useMemo<AuthState>(() => {
    function applyToken(token: string): void {
      const decoded = decodeToken(token);
      if (!decoded) throw new Error("Received an invalid token from the server");
      localStorage.setItem(STORAGE_KEY, token);
      setAuthToken(token);
      setClaims(decoded);
    }

    return {
      userId: claims?.sub ?? null,
      tenantId: claims?.tenant_id ?? null,
      tenantName: claims?.tenant_name ?? null,
      role: claims?.role ?? null,
      email: claims?.email ?? null,
      name: claims?.name ?? null,
      isAuthenticated: claims !== null,
      login: async (email: string, password: string) => {
        const { token } = await loginRequest(email, password);
        applyToken(token);
      },
      requestSignupOtp: async (
        organizationName: string,
        email: string,
        password: string,
        name: string,
      ) => {
        await requestSignupOtpRequest(organizationName, email, password, name);
      },
      verifySignupOtp: async (email: string, code: string) => {
        const { token } = await verifySignupOtpRequest(email, code);
        applyToken(token);
      },
      changePassword: async (currentPassword: string, newPassword: string) => {
        await changePasswordRequest(currentPassword, newPassword);
      },
      requestChangeEmailOtp: async (newEmail: string, currentPassword: string) => {
        await requestChangeEmailOtpRequest(newEmail, currentPassword);
      },
      verifyChangeEmailOtp: async (code: string) => {
        const { token } = await verifyChangeEmailOtpRequest(code);
        applyToken(token);
      },
      logout: () => {
        localStorage.removeItem(STORAGE_KEY);
        setAuthToken(null);
        setClaims(null);
      },
    };
  }, [claims]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
