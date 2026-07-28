import { apiClient } from "./client";

export interface MemberRecord {
  user_id: string;
  name: string;
  email: string;
  role: "admin" | "member";
}

export async function listMembers(): Promise<MemberRecord[]> {
  const { data } = await apiClient.get<MemberRecord[]>("/auth/members");
  return data;
}

export async function updateMember(
  userId: string,
  patch: { name?: string; email?: string; password?: string },
): Promise<MemberRecord> {
  const { data } = await apiClient.patch<MemberRecord>(`/auth/members/${userId}`, patch);
  return data;
}

export async function deleteMember(userId: string): Promise<void> {
  await apiClient.delete(`/auth/members/${userId}`);
}
