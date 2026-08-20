export function BalanceCard({
  label,
  value,
  icon,
  tone = "forest",
  subtext,
}: {
  label: string;
  value: string;
  icon: string;
  tone?: "gold" | "forest";
  subtext?: string;
}) {
  const styles =
    tone === "gold"
      ? {
          card: "bg-gradient-to-br from-amber-300 to-amber-500 text-forest-950",
          label: "text-forest-900/80",
          lock: "text-forest-900/60",
          subtext: "text-forest-900/70",
        }
      : {
          card: "bg-gradient-to-br from-forest-800 to-forest-950 text-white",
          label: "text-forest-100/80",
          lock: "text-forest-100/60",
          subtext: "text-forest-100/75",
        };

  return (
    <div className={`rounded-2xl p-5 shadow-warm ${styles.card}`}>
      <div className="flex items-center justify-between">
        <span className="text-lg">{icon}</span>
        <span className={styles.lock} aria-hidden="true">🔒</span>
      </div>
      <p className={`mt-2 text-sm font-semibold ${styles.label}`}>{label}</p>
      <p className="mt-1 font-display text-3xl font-extrabold tracking-tight">{value}</p>
      {subtext ? <p className={`mt-1 text-xs font-medium ${styles.subtext}`}>{subtext}</p> : null}
    </div>
  );
}