import { apiClient } from "./client";
import type { AuditLogEntry } from "../types";

export async function listAuditLog(): Promise<AuditLogEntry[]> {
  const { data } = await apiClient.get<AuditLogEntry[]>("/audit-log");
  return data;
}
