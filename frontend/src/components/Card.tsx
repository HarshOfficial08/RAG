import type { HTMLAttributes } from "react";

export function Card({ className = "", ...props }: Readonly<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div
      className={`rounded-lg border border-surface-border bg-surface-container p-4 ${className}`}
      {...props}
    />
  );
}
