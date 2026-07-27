import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef } from "react";
import { listDocuments, uploadDocument } from "../api/documents";
import { Badge } from "../components/Badge";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import type { DocumentStatus } from "../types";

const STATUS_VARIANT: Record<DocumentStatus, "success" | "warning" | "danger"> = {
  indexed: "success",
  processing: "warning",
  failed: "danger",
};

export function Documents() {
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
    refetchInterval: 5000, // simple polling for processing -> indexed transitions
  });

  const upload = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents"] }),
  });

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) upload.mutate(file);
    event.target.value = "";
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Document Library</h1>
        <Button onClick={() => fileInput.current?.click()} disabled={upload.isPending}>
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
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-b border-surface-border last:border-0">
                  <td className="p-3">{doc.filename}</td>
                  <td className="p-3">
                    <Badge variant={STATUS_VARIANT[doc.status]}>{doc.status}</Badge>
                  </td>
                  <td className="p-3">
                    {doc.piiMasked && <Badge variant="success">PII Masked</Badge>}
                  </td>
                  <td className="p-3 text-on-surface-muted">{doc.uploadedAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      <div className="flex flex-col gap-3 md:hidden">
        {documents.map((doc) => (
          <Card key={doc.id}>
            <p className="font-medium">{doc.filename}</p>
            <div className="mt-2 flex gap-2">
              <Badge variant={STATUS_VARIANT[doc.status]}>{doc.status}</Badge>
              {doc.piiMasked && <Badge variant="success">PII Masked</Badge>}
            </div>
          </Card>
        ))}
      </div>

      {!isLoading && documents.length === 0 && (
        <p className="text-on-surface-muted">No documents uploaded yet.</p>
      )}
    </div>
  );
}
