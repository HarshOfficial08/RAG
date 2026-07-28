import { useQuery } from "@tanstack/react-query";
import { ShieldAlert, ShieldCheck } from "lucide-react";
import { listAuditLog } from "../api/audit";
import { Badge } from "../components/Badge";
import { Card } from "../components/Card";

export function AuditLog() {
  const { data: entries = [], isLoading } = useQuery({
    queryKey: ["audit-log"],
    queryFn: listAuditLog,
  });

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold">Audit Log</h1>
      {isLoading && <p className="text-on-surface-muted">Loading...</p>}

      <div className="hidden md:block">
        <Card className="p-0">
          <table className="w-full text-left text-sm">
            <thead className="text-on-surface-muted">
              <tr className="border-b border-surface-border">
                <th className="p-3 font-normal">Timestamp</th>
                <th className="p-3 font-normal">User</th>
                <th className="p-3 font-normal">Question</th>
                <th className="p-3 font-normal">Masking</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id} className="border-b border-surface-border last:border-0">
                  <td className="p-3 font-mono text-xs text-on-surface-muted">{entry.timestamp}</td>
                  <td className="p-3">{entry.userId}</td>
                  <td className="p-3">{entry.question}</td>
                  <td className="p-3">
                    <Badge
                      variant={entry.maskingTriggered ? "warning" : "neutral"}
                      icon={entry.maskingTriggered ? ShieldAlert : ShieldCheck}
                    >
                      {entry.maskingTriggered ? "Triggered" : "None"}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>

      <div className="flex flex-col gap-3 md:hidden">
        {entries.map((entry) => (
          <Card key={entry.id}>
            <p className="font-mono text-xs text-on-surface-muted">{entry.timestamp}</p>
            <p className="mt-1">{entry.question}</p>
            <div className="mt-2">
              <Badge
                variant={entry.maskingTriggered ? "warning" : "neutral"}
                icon={entry.maskingTriggered ? ShieldAlert : ShieldCheck}
              >
                {entry.maskingTriggered ? "Triggered" : "None"}
              </Badge>
            </div>
          </Card>
        ))}
      </div>

      {!isLoading && entries.length === 0 && (
        <p className="text-on-surface-muted">No queries logged yet.</p>
      )}
    </div>
  );
}
