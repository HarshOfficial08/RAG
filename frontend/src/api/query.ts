import { apiClient } from "./client";
import type { QueryResponse } from "../types";

export async function askQuestion(question: string): Promise<QueryResponse> {
  const { data } = await apiClient.post<QueryResponse>("/query", { question });
  return data;
}
