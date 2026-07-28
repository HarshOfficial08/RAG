import { CheckCircle2, KeyRound, Mail } from "lucide-react";
import { useState, type SubmitEvent } from "react";
import { Link } from "react-router-dom";
import { forgotPassword } from "../api/auth";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Input } from "../components/Input";

export function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await forgotPassword(email);
    } finally {
      // Always show the same generic confirmation, whether or not the email
      // is registered — see backend/app/api/auth.py for why.
      setSubmitting(false);
      setSubmitted(true);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <h1 className="mb-1 flex items-center gap-2 text-lg font-semibold">
          <KeyRound size={20} className="text-accent" />
          Reset your password
        </h1>
        {submitted ? (
          <p className="mb-6 flex items-start gap-2 text-sm text-on-surface-muted">
            <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-accent" />
            If that email is registered, we've sent a reset link — check your inbox.
          </p>
        ) : (
          <>
            <p className="mb-6 text-sm text-on-surface-muted">
              Enter your account email and we'll send you a reset link.
            </p>
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Button type="submit" disabled={submitting}>
                <Mail size={16} />
                {submitting ? "Sending..." : "Send reset link"}
              </Button>
            </form>
          </>
        )}
        <p className="mt-4 text-center text-sm text-on-surface-muted">
          <Link to="/login" className="text-accent hover:underline">
            Back to sign in
          </Link>
        </p>
      </Card>
    </div>
  );
}
