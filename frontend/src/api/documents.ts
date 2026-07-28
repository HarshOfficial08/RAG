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

export async function deleteDocument(id: string): Promise<void> {
  await apiClient.delete(`/documents/${id}`);
}

export async function getDocumentPreview(id: string): Promise<{ filename: string; text: string }> {
  const { data } = await apiClient.get<{ filename: string; text: string }>(
    `/documents/${id}/preview`,
  );
  return data;
}
