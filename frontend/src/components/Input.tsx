import { Eye, EyeOff } from "lucide-react";
import { useState, type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function Input({
  label,
  error,
  id,
  type,
  className = "",
  ...props
}: Readonly<InputProps>) {
  const [visible, setVisible] = useState(false);
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
  const isPassword = type === "password";

  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor={inputId}
        className="font-mono text-xs uppercase tracking-wide text-on-surface-muted"
      >
        {label}
      </label>
      <div className="relative">
        <input
          id={inputId}
          type={isPassword && visible ? "text" : type}
          className={`w-full rounded-md border border-surface-border bg-surface px-3 py-2 text-sm text-on-surface focus:border-accent focus:outline-none ${isPassword ? "pr-10" : ""} ${className}`}
          {...props}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setVisible((v) => !v)}
            className="absolute inset-y-0 right-0 flex items-center px-3 text-on-surface-muted hover:text-on-surface"
            aria-label={visible ? "Hide password" : "Show password"}
          >
            {visible ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        )}
      </div>
      {error && <span className="text-xs text-danger">{error}</span>}
    </div>
  );
}
