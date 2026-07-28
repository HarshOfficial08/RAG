import type { LucideIcon } from "lucide-react";

type Variant = "neutral" | "success" | "warning" | "danger";

interface BadgeProps {
  children: React.ReactNode;
  variant?: Variant;
  icon?: LucideIcon;
}

const VARIANT_CLASSES: Record<Variant, string> = {
  neutral: "border-surface-border text-on-surface-muted",
  success: "border-accent text-accent",
  warning: "border-warning text-warning",
  danger: "border-danger text-danger",
};

export function Badge({ children, variant = "neutral", icon: Icon }: Readonly<BadgeProps>) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 font-mono text-xs uppercase tracking-wide ${VARIANT_CLASSES[variant]}`}
    >
      {Icon && <Icon size={12} />}
      {children}
    </span>
  );
}
