import { useState, type SubmitEvent } from "react";
import { UserPlus, Users } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Input } from "../components/Input";
import { inviteTeammate } from "../api/auth";
import { useAuth } from "../auth/useAuth";

function errorStatus(err: unknown): number | undefined {
  return (err as { response?: { status?: number } })?.response?.status;
}

export function OrgMembers() {
  const { tenantName } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: SubmitEvent) {
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
        `${email} has been added to ${tenantName ?? "your organization"} — they can sign in with the password you set.`,
      );
      setName("");
      setEmail("");
      setPassword("");
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
    <div className="flex max-w-xl flex-col gap-6">
      <div className="flex items-center gap-3">
        <Users size={22} className="text-accent" />
        <h1 className="text-xl font-semibold">Organization Members</h1>
      </div>

      <p className="text-sm text-on-surface-muted">
        Add a new member to{" "}
        <span className="font-medium text-on-surface">{tenantName ?? "your organization"}</span>.
        They join immediately with the credentials below — no email verification needed, since
        you're vouching for them directly.
      </p>

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

      <Card>
        <h2 className="mb-2 font-medium text-on-surface-muted text-sm uppercase tracking-wide">
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
    </div>
  );
}
