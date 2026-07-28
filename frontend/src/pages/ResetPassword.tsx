import { AlertTriangle, KeyRound, Save } from "lucide-react";
import { useState, type SubmitEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { resetPassword } from "../api/auth";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Input } from "../components/Input";

export function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const navigate = useNavigate();

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    setError(null);

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    setSubmitting(true);
    try {
      await resetPassword(token, newPassword);
      navigate("/login");
    } catch {
      setError("This reset link is invalid or has expired.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-sm">
          <p className="flex items-start gap-2 text-sm text-danger">
            <AlertTriangle size={16} className="mt-0.5 shrink-0" />
            This reset link is missing its token. Request a new one from{" "}
            <Link to="/forgot-password" className="text-accent hover:underline">
              the forgot password page
            </Link>
            .
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <h1 className="mb-1 flex items-center gap-2 text-lg font-semibold">
          <KeyRound size={20} className="text-accent" />
          Set a new password
        </h1>
        <p className="mb-6 text-sm text-on-surface-muted">
          Choose a new password for your account.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="New password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            minLength={8}
            required
          />
          <Input
            label="Confirm new password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            minLength={8}
            required
          />
          {error && <p className="text-sm text-danger">{error}</p>}
          <Button type="submit" disabled={submitting}>
            <Save size={16} />
            {submitting ? "Saving..." : "Save new password"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
