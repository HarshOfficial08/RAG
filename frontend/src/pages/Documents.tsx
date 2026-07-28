import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CheckCircle2,
  Clock,
  Eye,
  FileText,
  ShieldCheck,
  Trash2,
  Upload,
  X,
  XCircle,
  type LucideIcon,
} from "lucide-react";
import { useRef, useState } from "react";
import {
  deleteDocument,
  getDocumentPreview,
  listDocuments,
  uploadDocument,
} from "../api/documents";
import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import type { DocumentRecord, DocumentStatus } from "../types";

const STATUS_VARIANT: Record<DocumentStatus, "success" | "warning" | "danger"> = {
  indexed: "success",
  processing: "warning",
  failed: "danger",
};

const STATUS_ICON: Record<DocumentStatus, LucideIcon> = {
  indexed: CheckCircle2,
  processing: Clock,
  failed: XCircle,
};

export function Documents() {
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const [previewDoc, setPreviewDoc] = useState<DocumentRecord | null>(null);

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
    refetchInterval: 5000, // simple polling for processing -> indexed transitions
  });

  const upload = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  const remove = useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  const preview = useQuery({
    queryKey: ["document-preview", previewDoc?.id],
    queryFn: () => getDocumentPreview(previewDoc!.id),
    enabled: previewDoc !== null,
  });

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) upload.mutate(file);
    event.target.value = "";
  }

  function handleDelete(doc: DocumentRecord) {
    if (window.confirm(`Delete "${doc.filename}"? This cannot be undone.`)) {
      remove.mutate(doc.id);
    }
  }

  return (
    <>
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">Document Library</h1>
          <Button onClick={() => fileInput.current?.click()} disabled={upload.isPending}>
            <Upload size={16} />
            {upload.isPending ? "Uploading..." : "Upload document"}
          </Button>
          <input ref={fileInput} type="file" className="hidden" onChange={handleFileChange} />
        </div>

        {isLoading && <p className="text-on-surface-muted">Loading documents...</p>}

        {/* Table on md+, stacked cards below md — no horizontally-scrolling table with no affordance. */}
        <div className="hidden md:block">
          <Card className="p-0">
            <table className="w-full text-left text-sm">
              <thead className="text-on-surface-muted">
                <tr className="border-b border-surface-border">
                  <th className="p-3 font-normal">Filename</th>
                  <th className="p-3 font-normal">Status</th>
                  <th className="p-3 font-normal">Security</th>
                  <th className="p-3 font-normal">Uploaded</th>
                  <th className="p-3 font-normal">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} className="border-b border-surface-border last:border-0">
                    <td className="flex items-center gap-2 p-3">
                      <FileText size={16} className="text-on-surface-muted" />
                      {doc.filename}
                    </td>
                    <td className="p-3">
                      <Badge variant={STATUS_VARIANT[doc.status]} icon={STATUS_ICON[doc.status]}>
                        {doc.status}
                      </Badge>
                    </td>
                    <td className="p-3">
                      {doc.piiMasked && (
                        <Badge variant="success" icon={ShieldCheck}>
                          PII Masked
                        </Badge>
                      )}
                    </td>
                    <td className="p-3 text-on-surface-muted">{doc.uploadedAt}</td>
                    <td className="p-3 text-right">
                      <div className="flex items-center justify-end gap-3">
                        <button
                          type="button"
                          onClick={() => setPreviewDoc(doc)}
                          aria-label={`Preview ${doc.filename}`}
                          className="text-on-surface-muted transition hover:text-accent"
                        >
                          <Eye size={16} />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(doc)}
                          disabled={remove.isPending}
                          aria-label={`Delete ${doc.filename}`}
                          className="text-on-surface-muted transition hover:text-danger disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>

        <div className="flex flex-col gap-3 md:hidden">
          {documents.map((doc) => (
            <Card key={doc.id}>
              <div className="flex items-start justify-between gap-2">
                <p className="flex items-center gap-2 font-medium">
                  <FileText size={16} className="text-on-surface-muted" />
                  {doc.filename}
                </p>
                <div className="flex shrink-0 items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setPreviewDoc(doc)}
                    aria-label={`Preview ${doc.filename}`}
                    className="text-on-surface-muted transition hover:text-accent"
                  >
                    <Eye size={16} />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(doc)}
                    disabled={remove.isPending}
                    aria-label={`Delete ${doc.filename}`}
                    className="text-on-surface-muted transition hover:text-danger disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <div className="mt-2 flex gap-2">
                <Badge variant={STATUS_VARIANT[doc.status]} icon={STATUS_ICON[doc.status]}>
                  {doc.status}
                </Badge>
                {doc.piiMasked && (
                  <Badge variant="success" icon={ShieldCheck}>
                    PII Masked
                  </Badge>
                )}
              </div>
            </Card>
          ))}
        </div>

        {!isLoading && documents.length === 0 && (
          <p className="text-on-surface-muted">No documents uploaded yet.</p>
        )}
      </div>

      {previewDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <button
            type="button"
            aria-label="Close preview backdrop"
            className="fixed inset-0 bg-black/60 border-0 cursor-default"
            onClick={() => setPreviewDoc(null)}
          />
          <Card className="relative z-10 flex max-h-[80vh] w-full max-w-2xl flex-col gap-4 p-0">
            <div className="flex items-center justify-between border-b border-surface-border p-4">
              <h2 className="flex items-center gap-2 font-medium">
                <FileText size={16} className="text-on-surface-muted" />
                {previewDoc.filename}
              </h2>
              <button
                type="button"
                onClick={() => setPreviewDoc(null)}
                aria-label="Close preview"
                className="text-on-surface-muted transition hover:text-on-surface"
              >
                <X size={18} />
              </button>
            </div>

            <div className="overflow-y-auto p-4 pt-0">
              {preview.isLoading && <p className="text-on-surface-muted">Loading preview...</p>}
              {preview.isError && (
                <p className="text-danger">
                  Unable to load a preview for this document. It may still be processing, or it may
                  no longer exist.
                </p>
              )}
              {preview.data && (
                <pre className="whitespace-pre-wrap break-words font-sans text-sm text-on-surface">
                  {preview.data.text}
                </pre>
              )}
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
