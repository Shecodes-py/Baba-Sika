import type { ReactNode } from "react";

export function BalanceCard({
  label,
  value,
  accent = "brand",
  footer,
}: {
  label: string;
  value: string;
  accent?: "brand" | "accent";
  footer?: ReactNode;
}) {
  const dot = accent === "brand" ? "bg-brand" : "bg-accent";

  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center gap-2 text-sm font-medium text-muted">
        <span className={`h-2.5 w-2.5 rounded-full ${dot}`} />
        {label}
      </div>
      <p className="mt-2 text-2xl font-bold tracking-tight">{value}</p>
      {footer ? <div className="mt-2 text-sm text-muted">{footer}</div> : null}
    </div>
  );
}
