import { apiClient } from "./client";

export interface LoginResponse {
  token: string;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>("/auth/login", { email, password });
  return data;
}

// Signup is a two-step, email-verified flow: request-otp stashes the
// pending signup and emails a 6-digit code (nothing is created yet);
// verify-otp checks the code and actually creates the account, returning a
// token exactly like login/the old one-step signup did.
export async function requestSignupOtp(
  organizationName: string,
  email: string,
  password: string,
  name: string,
): Promise<void> {
  await apiClient.post("/auth/signup/request-otp", {
    organization_name: organizationName,
    email,
    password,
    name,
  });
}

export async function verifySignupOtp(email: string, code: string): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>("/auth/signup/verify-otp", {
    email,
    code,
  });
  return data;
}

export async function forgotPassword(email: string): Promise<void> {
  await apiClient.post("/auth/forgot-password", { email });
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  await apiClient.post("/auth/reset-password", { token, new_password: newPassword });
}

export async function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<void> {
  await apiClient.post("/auth/change-password", {
    current_password: currentPassword,
    new_password: newPassword,
  });
}

// Settings: two-step, OTP-verified email change — mirrors the
// request-otp/verify-otp shape of signup above, except both steps are
// authenticated (the account being changed always comes from the bearer
// token, never a request body field).
export async function requestChangeEmailOtp(
  newEmail: string,
  currentPassword: string,
): Promise<void> {
  await apiClient.post("/auth/change-email/request-otp", {
    new_email: newEmail,
    current_password: currentPassword,
  });
}

export async function verifyChangeEmailOtp(code: string): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>("/auth/change-email/verify-otp", {
    code,
  });
  return data;
}

// Admin-only: adds a teammate to the caller's own organization, active
// immediately with the email/name/password given here — no email-OTP step,
// since an admin vouching for a known teammate is treated as sufficient
// verification (unlike public signup).
export async function inviteTeammate(
  email: string,
  password: string,
  name: string,
): Promise<void> {
  await apiClient.post("/auth/invite", { email, password, name });
}
