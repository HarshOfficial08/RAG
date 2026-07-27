export type DocumentStatus = "processing" | "indexed" | "failed";

export interface DocumentRecord {
  id: string;
  filename: string;
  status: DocumentStatus;
  uploadedAt: string;
  piiMasked: boolean;
  failureReason?: string;
}

export interface QuerySource {
  documentId: string;
  filename: string;
  chunkIndex: number;
}

export interface QueryResponse {
  answer: string;
  sources: QuerySource[];
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  question: string;
  maskingTriggered: boolean;
}
