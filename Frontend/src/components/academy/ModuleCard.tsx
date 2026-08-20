import type { AcademyModule } from "@/lib/academyContent";

export function ModuleCard({ moduleTopic }: { moduleTopic: AcademyModule }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-6">
      <span className="text-xs font-semibold uppercase tracking-wide text-muted">Module topic</span>
      <h3 className="mt-1 text-lg font-semibold">{moduleTopic.title}</h3>
      <p className="mt-1 text-sm text-muted">{moduleTopic.subtitle}</p>
      <p className="mt-4 rounded-xl bg-accent-light px-4 py-3 text-sm text-foreground">{moduleTopic.body}</p>
    </div>
  );
}
