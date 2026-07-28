import { useState } from "react";
import { Pencil, Trash2, UserPlus, Users, X, ShieldCheck, User } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Input } from "../components/Input";
import { Badge } from "../components/Badge";
import { inviteTeammate } from "../api/auth";
import { listMembers, updateMember, deleteMember, type MemberRecord } from "../api/members";
import { useAuth } from "../auth/useAuth";

function errorStatus(err: unknown): number | undefined {
  return (err as { response?: { status?: number } })?.response?.status;
}

// ─── Add Member Form ─────────────────────────────────────────────────────────

function AddMemberForm({ onAdded }: { onAdded: () => void }) {
  const { tenantName } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    try {
      await inviteTeammate(email, password, name);
      setSuccess(
        `${email} has been added to ${tenantName ?? "your organization"}.`,
      );
      setName("");
      setEmail("");
      setPassword("");
      onAdded();
    } catch (err) {
      const status = errorStatus(err);
      setError(
        status === 409
          ? "An account with that email already exists."
          : status === 403
            ? "Only an organization admin can add members."
            : "Something went wrong adding this member.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <h2 className="mb-4 flex items-center gap-2 font-medium">
        <UserPlus size={16} className="text-accent" />
        Add member
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Full name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoComplete="name"
          required
        />
        <Input
          label="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
        />
        <Input
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
        />
        {error && <p className="text-sm text-danger">{error}</p>}
        {success && <p className="text-sm text-accent">{success}</p>}
        <Button type="submit" disabled={submitting} className="self-start">
          {submitting ? "Adding..." : "Add member"}
        </Button>
      </form>
    </Card>
  );
}

// ─── Edit Member Modal ────────────────────────────────────────────────────────

function EditMemberModal({
  member,
  onClose,
  onSaved,
}: {
  member: MemberRecord;
  onClose: () => void;
  onSaved: () => void;
}) {
  const qc = useQueryClient();
  const [name, setName] = useState(member.name);
  const [email, setEmail] = useState(member.email);
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => {
      const patch: { name?: string; email?: string; password?: string } = {};
      if (name !== member.name) patch.name = name;
      if (email !== member.email) patch.email = email;
      if (password.length > 0) patch.password = password;
      return updateMember(member.user_id, patch);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["members"] });
      onSaved();
      onClose();
    },
    onError: (err) => {
      const status = errorStatus(err);
      setError(
        status === 409
          ? "That email is already in use."
          : status === 404
            ? "Member not found."
            : "Something went wrong updating this member.",
      );
    },
  });

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <Card
        className="w-full max-w-md"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-2 font-medium">
            <Pencil size={16} className="text-accent" />
            Edit member
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-on-surface-muted hover:text-on-surface"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (password && password.length < 8) {
              setError("New password must be at least 8 characters.");
              return;
            }
            setError(null);
            mutation.mutate();
          }}
          className="flex flex-col gap-4"
        >
          <Input
            label="Full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="New password (leave blank to keep unchanged)"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            minLength={8}
          />
          {error && <p className="text-sm text-danger">{error}</p>}
          <div className="flex justify-end gap-3">
            <Button type="button" onClick={onClose} className="bg-transparent border border-surface-border text-on-surface hover:bg-surface-container-high">
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving..." : "Save changes"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

// ─── Member Row ───────────────────────────────────────────────────────────────

function MemberRow({
  member,
  isSelf,
  onEdit,
  onDelete,
}: {
  member: MemberRecord;
  isSelf: boolean;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <tr className="border-b border-surface-border last:border-0">
      <td className="flex items-center gap-3 p-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-surface-container-high text-on-surface-muted">
          {member.role === "admin" ? <ShieldCheck size={14} className="text-accent" /> : <User size={14} />}
        </div>
        <div>
          <p className="font-medium leading-tight">
            {member.name}
            {isSelf && (
              <span className="ml-2 text-xs text-on-surface-muted">(you)</span>
            )}
          </p>
          <p className="text-xs text-on-surface-muted">{member.email}</p>
        </div>
      </td>
      <td className="p-3">
        <Badge variant={member.role === "admin" ? "success" : "neutral"}>
          {member.role}
        </Badge>
      </td>
      <td className="p-3 text-right">
        <div className="flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onEdit}
            aria-label={`Edit ${member.name}`}
            className="text-on-surface-muted transition hover:text-accent"
          >
            <Pencil size={15} />
          </button>
          <button
            type="button"
            onClick={onDelete}
            disabled={isSelf}
            aria-label={isSelf ? "Cannot remove yourself" : `Remove ${member.name}`}
            title={isSelf ? "You cannot remove your own account" : undefined}
            className="text-on-surface-muted transition hover:text-danger disabled:cursor-not-allowed disabled:opacity-30"
          >
            <Trash2 size={15} />
          </button>
        </div>
      </td>
    </tr>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export function OrgMembers() {
  const { tenantName, userId } = useAuth();
  const qc = useQueryClient();
  const [editingMember, setEditingMember] = useState<MemberRecord | null>(null);

  const { data: members = [], isLoading } = useQuery({
    queryKey: ["members"],
    queryFn: listMembers,
  });

  const removeMutation = useMutation({
    mutationFn: deleteMember,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["members"] }),
  });

  function handleDelete(member: MemberRecord) {
    if (
      window.confirm(
        `Remove ${member.name} (${member.email}) from the organization?\n\nThis cannot be undone.`,
      )
    ) {
      removeMutation.mutate(member.user_id);
    }
  }

  return (
    <div className="flex max-w-2xl flex-col gap-6">
      <div className="flex items-center gap-3">
        <Users size={22} className="text-accent" />
        <h1 className="text-xl font-semibold">Organization Members</h1>
        {tenantName && (
          <span className="ml-auto">
            <Badge variant="success">{tenantName}</Badge>
          </span>
        )}
      </div>

      {/* Members list */}
      <Card className="p-0">
        {isLoading ? (
          <p className="p-4 text-sm text-on-surface-muted">Loading members…</p>
        ) : members.length === 0 ? (
          <p className="p-4 text-sm text-on-surface-muted">No members yet.</p>
        ) : (
          <table className="w-full text-left text-sm">
            <thead className="text-on-surface-muted">
              <tr className="border-b border-surface-border">
                <th className="p-3 font-normal">Member</th>
                <th className="p-3 font-normal">Role</th>
                <th className="p-3 font-normal">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {members.map((m) => (
                <MemberRow
                  key={m.user_id}
                  member={m}
                  isSelf={m.user_id === userId}
                  onEdit={() => setEditingMember(m)}
                  onDelete={() => handleDelete(m)}
                />
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {/* Permission summary */}
      <Card>
        <h2 className="mb-2 text-sm font-medium uppercase tracking-wide text-on-surface-muted">
          Member permissions
        </h2>
        <ul className="flex flex-col gap-2 text-sm text-on-surface-muted">
          <li className="flex items-center gap-2">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent" />
            Can query documents using Ask a Question
          </li>
          <li className="flex items-center gap-2">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-danger" />
            Cannot upload or delete documents
          </li>
          <li className="flex items-center gap-2">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-danger" />
            Cannot add or manage members
          </li>
          <li className="flex items-center gap-2">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-danger" />
            Cannot access Settings or Audit Log
          </li>
        </ul>
      </Card>

      {/* Add member form */}
      <AddMemberForm onAdded={() => qc.invalidateQueries({ queryKey: ["members"] })} />

      {/* Edit modal */}
      {editingMember && (
        <EditMemberModal
          member={editingMember}
          onClose={() => setEditingMember(null)}
          onSaved={() => setEditingMember(null)}
        />
      )}
    </div>
  );
}
