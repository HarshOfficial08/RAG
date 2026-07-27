import { apiClient } from "./client";
import type { DocumentRecord } from "../types";

export async function listDocuments(): Promise<DocumentRecord[]> {
  const { data } = await apiClient.get<DocumentRecord[]>("/documents");
  return data;
}

export async function uploadDocument(file: File): Promise<DocumentRecord> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<DocumentRecord>("/documents", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
