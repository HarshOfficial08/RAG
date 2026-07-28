import { useState, type SubmitEvent } from "react";
import { KeyRound, Mail, Users } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Input } from "../components/Input";
import { useAuth } from "../auth/useAuth";
import { useNavigate } from "react-router-dom";

function errorStatus(err: unknown): number | undefined {
  return (err as { response?: { status?: number } })?.response?.status;
}

function ChangePasswordCard() {
  const { changePassword } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (newPassword.length < 8) {
      setError("New password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New password and confirmation don't match.");
      return;
    }

    setSubmitting(true);
    try {
      await changePassword(currentPassword, newPassword);
      setSuccess("Password updated.");
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(
        errorStatus(err) === 400
          ? "Current password is incorrect."
          : "Something went wrong updating your password.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card>
      <h2 className="mb-3 flex items-center gap-2 font-medium">
        <KeyRound size={16} className="text-accent" />
        Change password
      </h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          label="Current password"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
        <Input
          label="New password"
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
        />
        <Input
          label="Confirm new password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          autoComplete="new-password"
          minLength={8}
          required
        />
        {error && <p className="text-sm text-danger">{error}</p>}
        {success && <p className="text-sm text-accent">{success}</p>}
        <Button type="submit" disabled={submitting} className="self-start">
          {submitting ? "Updating..." : "Update password"}
        </Button>
      </form>
    </Card>
  );
}

type ChangeEmailStep = "request" | "verify";

function ChangeEmailCard() {
  const { requestChangeEmailOtp, verifyChangeEmailOtp, email: currentEmail } = useAuth();
  const [step, setStep] = useState<ChangeEmailStep>("request");
  const [newEmail, setNewEmail] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleRequestSubmit(event: SubmitEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    setSubmitting(true);
    try {
      await requestChangeEmailOtp(newEmail, currentPassword);
      setStep("verify");
    } catch (err) {
      const status = errorStatus(err);
      setError(
        status === 400
          ? "Current password is incorrect."
          : status === 409
            ? "An account with that email already exists."
            : "Something went wrong sending the verification code.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVerifySubmit(event: SubmitEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    setSubmitting(true);
    try {
      await verifyChangeEmailOtp(code);
      setSuccess(`Your email has been updated to ${newEmail}.`);
      setStep("request");
      setNewEmail("");
      setCurrentPassword("");
      setCode("");
    } catch (err) {
      setError(
        errorStatus(err) === 400
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
      await requestChangeEmailOtp(newEmail, currentPassword);
    } catch {
      setError("Couldn't resend the code. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (step === "verify") {
    return (
      <Card>
        <h2 className="mb-1 flex items-center gap-2 font-medium">
          <Mail size={16} className="text-accent" />
          Change email
        </h2>
        <p className="mb-4 text-sm text-on-surface-muted">
          We sent a 6-digit verification code to{" "}
          <span className="text-on-surface">{newEmail}</span>. Enter it below to confirm this as
          your new sign-in email.
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
          {success && <p className="text-sm text-accent">{success}</p>}
          <Button type="submit" disabled={submitting || code.length !== 6} className="self-start">
            {submitting ? "Verifying..." : "Verify and update email"}
          </Button>
        </form>
        <p className="mt-4 text-sm text-on-surface-muted">
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
        <p className="mt-2 text-sm text-on-surface-muted">
          <button
            type="button"
            onClick={() => {
              setStep("request");
              setError(null);
              setCode("");
            }}
            className="text-accent hover:underline"
          >
            Use a different email
          </button>
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="mb-1 flex items-center gap-2 font-medium">
        <Mail size={16} className="text-accent" />
        Change email
      </h2>
      {currentEmail && (
        <p className="mb-4 text-sm text-on-surface-muted">
          Currently signed in as <span className="text-on-surface">{currentEmail}</span>.
        </p>
      )}
      <form onSubmit={handleRequestSubmit} className="flex flex-col gap-4">
        <Input
          label="New email"
          type="email"
          value={newEmail}
          onChange={(e) => setNewEmail(e.target.value)}
          required
        />
        <Input
          label="Current password"
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
        {error && <p className="text-sm text-danger">{error}</p>}
        {success && <p className="text-sm text-accent">{success}</p>}
        <Button type="submit" disabled={submitting} className="self-start">
          {submitting ? "Sending code..." : "Send verification code"}
        </Button>
      </form>
    </Card>
  );
}

export function Settings() {
  const { role } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex max-w-xl flex-col gap-6">
      <h1 className="text-xl font-semibold">Settings</h1>

      <ChangePasswordCard />
      <ChangeEmailCard />

      {role === "admin" && (
        <Card>
          <h2 className="mb-1 flex items-center gap-2 font-medium">
            <Users size={16} className="text-accent" />
            Organization members
          </h2>
          <p className="mb-4 text-sm text-on-surface-muted">
            Add members to your organization so they can query your documents.
          </p>
          <Button className="self-start" onClick={() => navigate("/org/members")}>
            Manage members
          </Button>
        </Card>
      )}
    </div>
  );
}
