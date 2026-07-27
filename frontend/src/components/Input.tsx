import type { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function Input({ label, error, id, className = "", ...props }: InputProps) {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");
  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor={inputId}
        className="font-mono text-xs uppercase tracking-wide text-on-surface-muted"
      >
        {label}
      </label>
      <input
        id={inputId}
        className={`rounded-md border border-surface-border bg-surface px-3 py-2 text-sm text-on-surface focus:border-accent focus:outline-none ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-danger">{error}</span>}
    </div>
  );
}
