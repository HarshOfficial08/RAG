import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: "bg-accent text-black hover:bg-accent-hover",
  secondary:
    "bg-surface-container-high text-on-surface hover:brightness-110 border border-surface-border",
  ghost:
    "bg-transparent text-on-surface hover:bg-surface-container-high border border-surface-border",
  danger: "bg-danger text-white hover:brightness-110",
};

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  return (
    <button
      className={`rounded-md px-4 py-2 text-sm font-medium transition disabled:opacity-50 disabled:cursor-not-allowed ${VARIANT_CLASSES[variant]} ${className}`}
      {...props}
    />
  );
}
