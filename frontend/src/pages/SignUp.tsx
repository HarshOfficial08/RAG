import { UserPlus, ShieldCheck, MailCheck } from "lucide-react";
import { useState, type SubmitEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { Button } from "../components/Button";
import { Card } from "../components/Card";
import { Input } from "../components/Input";

type Step = "details" | "verify";

export function SignUp() {
  const { requestSignupOtp, verifySignupOtp } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>("details");
  const [organizationName, setOrganizationName] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleDetailsSubmit(event: SubmitEvent) {
    event.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setSubmitting(true);
    try {
      await requestSignupOtp(organizationName, email, password, name);
      setStep("verify");
    } catch (err) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      setError(
        status === 409
          ? "An account with that email already exists."
          : "Something went wrong creating your account.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVerifySubmit(event: SubmitEvent) {
    event.preventDefault();
    setError(null);

    setSubmitting(true);
    try {
      await verifySignupOtp(email, code);
      navigate("/documents");
    } catch (err) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      setError(
        status === 400
          ? "That code is invalid or has expired. Please request a new one."
          : "Something went wrong verifying your code.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleResend() {
    setError(null);
    setSubmitting(true);
    try {
      await requestSignupOtp(organizationName, email, password, name);
    } catch {
      setError("Couldn't resend the code. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (step === "verify") {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-sm">
          <h1 className="mb-1 flex items-center gap-2 text-lg font-semibold">
            <MailCheck size={20} className="text-accent" />
            Check your email
          </h1>
          <p className="mb-6 text-sm text-on-surface-muted">
            We sent a 6-digit verification code to <span className="text-on-surface">{email}</span>.
            Enter it below to finish creating your account.
          </p>
          <form onSubmit={handleVerifySubmit} className="flex flex-col gap-4">
            <Input
              label="Verification code"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
              required
            />
            {error && <p className="text-sm text-danger">{error}</p>}
            <Button type="submit" disabled={submitting || code.length !== 6}>
              <UserPlus size={16} />
              {submitting ? "Verifying..." : "Verify and create account"}
            </Button>
          </form>
          <p className="mt-4 text-center text-sm text-on-surface-muted">
            Didn't get a code?{" "}
            <button
              type="button"
              onClick={handleResend}
              disabled={submitting}
              className="text-accent hover:underline disabled:opacity-50"
            >
              Resend it
            </button>
          </p>
          <p className="mt-2 text-center text-sm text-on-surface-muted">
            <button
              type="button"
              onClick={() => {
                setStep("details");
                setError(null);
                setCode("");
              }}
              className="text-accent hover:underline"
            >
              Use a different email
            </button>
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-sm">
        <h1 className="mb-1 flex items-center gap-2 text-lg font-semibold">
          <ShieldCheck size={20} className="text-accent" />
          SecureRAG
        </h1>
        <p className="mb-6 text-sm text-on-surface-muted">
          Create a new organization workspace.
        </p>
        <form onSubmit={handleDetailsSubmit} className="flex flex-col gap-4">
          <Input
            label="Organization name"
            value={organizationName}
            onChange={(e) => setOrganizationName(e.target.value)}
            required
          />
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
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />
          {error && <p className="text-sm text-danger">{error}</p>}
          <Button type="submit" disabled={submitting}>
            <UserPlus size={16} />
            {submitting ? "Sending code..." : "Create account"}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-on-surface-muted">
          Already have an account?{" "}
          <Link to="/login" className="text-accent hover:underline">
            Sign in
          </Link>
        </p>
      </Card>
    </div>
  );
}
