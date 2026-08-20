"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { formatNaira } from "@/lib/format";

const SPLIT = { emergency: 0.4, retirement: 0.6 };
const STEP_SIZE = 25;

export type MoveMoneyMode = "sale" | "withdrawal";

export type MoveMoneyResult =
  | { kind: "sale"; amount: number; emergencyCut: number; retirementCut: number }
  | { kind: "withdrawal"; amount: number; remaining: number };

type Step = "amount" | "confirm" | "processing" | "success";

interface MoveMoneyModalProps {
  mode: MoveMoneyMode;
  initialAmount: number;
  availableAmount: number;
  available: { bank: number; emergency: number; retirement: number };
  onComplete: (result: MoveMoneyResult) => void;
  onClose: () => void;
}

function useCountUp(target: number, duration = 700): number {
  const [value, setValue] = useState(0);
  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(target * eased));
      if (progress < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);
  return value;
}

function AnimatedNaira({ value, className }: { value: number; className?: string }) {
  const display = useCountUp(Math.max(0, value));
  return <span className={className}>{formatNaira(display)}</span>;
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <path d="M6 6l12 12M18 6L6 18" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 13l4 4L19 7" />
    </svg>
  );
}

function ArrowIcon({ direction = "forward" }: { direction?: "forward" | "back" }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={`h-4 w-4 ${direction === "back" ? "rotate-180" : ""}`}
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

const CHECK_ITEMS = {
  sale: ["Checking your balance", "Splitting your money (40/60)", "Updating your balance"],
  withdrawal: ["Checking your balance", "Moving to your emergency fund", "Updating your balance"],
} as const;

export function MoveMoneyModal({
  mode,
  initialAmount,
  availableAmount,
  available,
  onComplete,
  onClose,
}: MoveMoneyModalProps) {
  const [step, setStep] = useState<Step>("amount");
  const [amount, setAmount] = useState(() => Math.min(initialAmount, availableAmount));
  const [checkProgress, setCheckProgress] = useState(0);

  const isSale = mode === "sale";
  const emergencyCut = Math.round(amount * SPLIT.emergency);
  const retirementCut = amount - emergencyCut;
  const checkItems = useMemo(() => CHECK_ITEMS[mode], [mode]);

  const newTotalSaved = useMemo(() => {
    const base = available.emergency + available.retirement;
    return isSale ? base + emergencyCut + retirementCut : base - amount;
  }, [available, isSale, emergencyCut, retirementCut, amount]);

  const title = "Move money with BabaSika";
  const subtitle = isSale ? "Automated 40% to safety / 60% to retirement split" : "Simulated emergency withdrawal";

  function clampAmount(next: number) {
    return Math.min(Math.max(0, next), Math.max(0, availableAmount));
  }

  function handleAmountChange(raw: string) {
    const digits = raw.replace(/\D/g, "");
    setAmount(clampAmount(digits ? Number.parseInt(digits, 10) : 0));
  }

  function bump(delta: number) {
    setAmount((prev) => clampAmount(prev + delta));
  }

  function handleConfirmMove() {
    const result: MoveMoneyResult = isSale
      ? { kind: "sale", amount, emergencyCut, retirementCut }
      : { kind: "withdrawal", amount, remaining: Math.max(0, availableAmount - amount) };
    onComplete(result);
    setCheckProgress(0);
    setStep("processing");
  }

  useEffect(() => {
    if (step !== "processing") return;
    const timers: number[] = [];
    for (let i = 0; i < checkItems.length; i += 1) {
      timers.push(window.setTimeout(() => setCheckProgress(i + 1), (i + 1) * 600));
    }
    timers.push(window.setTimeout(() => setStep("success"), checkItems.length * 600 + 450));
    return () => timers.forEach((id) => window.clearTimeout(id));
  }, [step, checkItems]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const stepIndex: Record<Step, number> = { amount: 0, confirm: 1, processing: 2, success: 3 };

  return (
    <div
      className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 px-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="flex max-h-[90vh] w-full max-w-md flex-col overflow-hidden rounded-2xl bg-surface shadow-2xl shadow-forest-950/30"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="px-6 pb-4 pt-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="font-display text-lg font-extrabold tracking-tight text-foreground">{title}</h2>
              <p className="mt-0.5 text-sm text-muted">{subtitle}</p>
            </div>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close"
              className="rounded-full p-2 text-muted transition-colors hover:bg-sand-100 hover:text-foreground"
            >
              <CloseIcon />
            </button>
          </div>
          <div className="mt-4 flex items-center gap-1.5">
            {(["amount", "confirm", "processing", "success"] as const).map((s, index) => (
              <div
                key={s}
                className={`h-1 flex-1 rounded-full transition-colors ${
                  index <= stepIndex[step] ? "bg-brand" : "bg-sand-200"
                }`}
              />
            ))}
          </div>
        </div>

        <div className="border-t border-border" />

        <div className="flex-1 overflow-y-auto px-6 py-5">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.18, ease: "easeOut" }}
            >
              {step === "amount" && (
                <section>
                  <div className="flex items-baseline justify-between text-xs font-bold uppercase tracking-wider text-muted">
                    <span>How much?</span>
                    <span className="normal-case tracking-normal font-semibold">
                      Available: <span className="text-foreground">{formatNaira(availableAmount)}</span>
                    </span>
                  </div>

                  <div className="mt-3 flex items-center justify-between gap-3 border border-border bg-sand-50 px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="font-display text-2xl font-extrabold text-muted">₦</span>
                      <input
                        inputMode="numeric"
                        autoFocus
                        value={amount === 0 ? "" : String(amount)}
                        onChange={(event) => handleAmountChange(event.target.value)}
                        placeholder="0"
                        aria-label="Amount to move"
                        className="w-full bg-transparent font-display text-3xl font-extrabold tracking-tight text-foreground outline-none placeholder:text-sand-400"
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <button
                        type="button"
                        onClick={() => bump(STEP_SIZE)}
                        aria-label="Increase amount"
                        className="flex h-6 w-7 items-center justify-center rounded-md text-sm font-bold text-forest-700 transition-colors hover:bg-sand-200"
                      >
                        ▲
                      </button>
                      <button
                        type="button"
                        onClick={() => bump(-STEP_SIZE)}
                        aria-label="Decrease amount"
                        className="flex h-6 w-7 items-center justify-center rounded-md text-sm font-bold text-forest-700 transition-colors hover:bg-sand-200"
                      >
                        ▼
                      </button>
                    </div>
                  </div>

                  {isSale ? (
                    <div className="mt-4 rounded-xl border border-border bg-brand-light/40 p-3">
                      <p className="px-1 text-xs font-bold uppercase tracking-wider text-forest-700">
                        Your money will be split
                      </p>
                      <div className="mt-2 grid grid-cols-2 gap-2">
                        <div className="rounded-lg bg-brand p-3 text-white">
                          <p className="font-display text-xl font-extrabold">
                            <AnimatedNaira value={emergencyCut} />
                          </p>
                          <p className="mt-0.5 text-xs font-bold uppercase tracking-wide text-forest-100">
                            40% Contingent
                          </p>
                          <p className="text-xs text-forest-200">Safety money</p>
                        </div>
                        <div className="rounded-lg bg-amber-400 p-3 text-forest-950">
                          <p className="font-display text-xl font-extrabold">
                            <AnimatedNaira value={retirementCut} />
                          </p>
                          <p className="mt-0.5 text-xs font-bold uppercase tracking-wide text-amber-800">
                            60% Retirement
                          </p>
                          <p className="text-xs text-amber-800/80">Future money</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-4 rounded-xl border border-danger-light bg-danger-light/50 p-4">
                      <p className="text-xs font-bold uppercase tracking-wider text-danger">Emergency withdrawal</p>
                      <p className="mt-2 font-display text-xl font-extrabold text-foreground">
                        You&apos;ll withdraw <AnimatedNaira value={amount} />
                      </p>
                      <p className="mt-1 text-sm text-muted">
                        Remaining in emergency:{" "}
                        <span className="font-semibold text-foreground">
                          {formatNaira(Math.max(0, availableAmount - amount))}
                        </span>
                      </p>
                    </div>
                  )}

                  <div className="mt-5 flex gap-3">
                    <button
                      type="button"
                      onClick={onClose}
                      className="rounded-full border border-border px-5 py-2.5 text-sm font-semibold text-muted transition-colors hover:border-sand-300 hover:text-foreground"
                    >
                      Cancel
                    </button>
                    <button
                      type="button"
                      disabled={amount <= 0 || amount > availableAmount}
                      onClick={() => setStep("confirm")}
                      className="flex flex-1 items-center justify-center gap-2 rounded-full bg-brand px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Review Move <ArrowIcon />
                    </button>
                  </div>
                </section>
              )}

              {step === "confirm" && (
                <section>
                  <p className="text-xs font-bold uppercase tracking-wider text-muted">Confirm transaction</p>
                  <h3 className="mt-2 font-display text-2xl font-extrabold tracking-tight text-foreground">
                    <AnimatedNaira value={amount} /> {isSale ? "will be moved" : "will be withdrawn"}
                  </h3>

                  <div className="mt-4 rounded-xl border border-border bg-sand-50 p-4">
                    {isSale ? (
                      <>
                        <div className="flex items-center justify-between text-sm">
                          <span className="flex items-center gap-2 font-semibold text-foreground">
                            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-brand text-white">
                              <CheckIcon />
                            </span>
                            {formatNaira(emergencyCut)} → Contingent (Safety)
                          </span>
                        </div>
                        <div className="my-3 border-t border-dashed border-sand-300" />
                        <div className="flex items-center justify-between text-sm">
                          <span className="flex items-center gap-2 font-semibold text-foreground">
                            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-amber-400 text-forest-950">
                              <CheckIcon />
                            </span>
                            {formatNaira(retirementCut)} → Retirement (Future)
                          </span>
                        </div>
                        <p className="mt-3 text-xs italic text-muted">This is your BabaSika 40/60 split.</p>
                      </>
                    ) : (
                      <>
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-semibold text-foreground">Withdrawing</span>
                          <span className="font-display text-xl font-extrabold">{formatNaira(amount)}</span>
                        </div>
                        <div className="my-3 border-t border-dashed border-sand-300" />
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-semibold text-foreground">New emergency balance</span>
                          <span className="font-bold text-foreground">
                            {formatNaira(Math.max(0, availableAmount - amount))}
                          </span>
                        </div>
                      </>
                    )}
                  </div>

                  <div className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">
                    🛡️ {isSale ? "Demo • Auto-split mode" : "Demo • Emergency mode"}
                  </div>

                  <div className="mt-5 flex gap-3">
                    <button
                      type="button"
                      onClick={() => setStep("amount")}
                      className="flex items-center justify-center gap-2 rounded-full border border-border px-5 py-2.5 text-sm font-semibold text-muted transition-colors hover:border-sand-300 hover:text-foreground"
                    >
                      <ArrowIcon direction="back" /> Go Back
                    </button>
                    <button
                      type="button"
                      onClick={handleConfirmMove}
                      className="flex flex-1 items-center justify-center gap-2 rounded-full bg-brand px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-brand-dark"
                    >
                      Confirm Move
                    </button>
                  </div>
                </section>
              )}

              {step === "processing" && (
                <section>
                  <h3 className="font-display text-xl font-extrabold tracking-tight text-foreground">
                    Moving your money…
                  </h3>
                  <p className="mt-1 text-sm text-muted">
                    Simulating your {isSale ? "auto-split" : "emergency withdrawal"} account
                  </p>

                  <ul className="mt-5 space-y-3">
                    {checkItems.map((label, index) => {
                      const done = index < checkProgress;
                      const active = index === checkProgress;
                      return (
                        <li
                          key={label}
                          className={`flex items-center gap-3 rounded-lg border px-3.5 py-2.5 transition-colors ${
                            done
                              ? "border-forest-200 bg-forest-50 text-forest-800"
                              : active
                                ? "border-border bg-sand-50 text-foreground"
                                : "border-border bg-surface text-muted/70"
                          }`}
                        >
                          <span
                            className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${
                              done
                                ? "bg-forest-600 text-white"
                                : active
                                  ? "border-2 border-brand"
                                  : "border-2 border-sand-200"
                            }`}
                          >
                            {done ? (
                              <CheckIcon />
                            ) : active ? (
                              <span className="h-3 w-3 animate-spin rounded-full border-2 border-brand border-t-transparent" />
                            ) : null}
                          </span>
                          <span className={`text-sm font-semibold ${done ? "" : active ? "" : ""}`}>{label}</span>
                        </li>
                      );
                    })}
                  </ul>
                </section>
              )}

              {step === "success" && (
                <section className="text-center">
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-forest-100">
                    <span className="flex h-10 w-10 items-center justify-center rounded-full bg-forest-600 text-white">
                      <CheckIcon />
                    </span>
                  </div>
                  <h3 className="mt-4 font-display text-2xl font-extrabold tracking-tight text-foreground">
                    {isSale ? "Money moved successfully." : "Withdrawal complete."}
                  </h3>
                  <p className="mt-1.5 text-sm text-muted">
                    Your {isSale ? "40/60 split has been simulated." : "emergency withdrawal has been simulated."}
                  </p>

                  <div className="mt-4 inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold text-amber-800">
                    🛡️ {isSale ? "Auto-split mode" : "Emergency mode"}
                  </div>

                  <div className="mt-5 rounded-xl border border-border bg-sand-50 p-4 text-left">
                    {isSale ? (
                      <>
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-semibold text-foreground">
                            {formatNaira(emergencyCut)} → Contingent (Safety)
                          </span>
                          <span className="text-success">+{formatNaira(emergencyCut)}</span>
                        </div>
                        <div className="my-3 border-t border-dashed border-sand-300" />
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-semibold text-foreground">
                            {formatNaira(retirementCut)} → Retirement (Future)
                          </span>
                          <span className="text-amber-700">+{formatNaira(retirementCut)}</span>
                        </div>
                        <div className="my-3 border-t border-dashed border-sand-300" />
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-semibold text-muted">New total saved</span>
                          <AnimatedNaira value={newTotalSaved} className="font-display text-lg font-extrabold text-foreground" />
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-semibold text-foreground">Withdrawn</span>
                          <span className="text-danger">-{formatNaira(amount)}</span>
                        </div>
                        <div className="my-3 border-t border-dashed border-sand-300" />
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-semibold text-muted">New emergency balance</span>
                          <AnimatedNaira
                            value={Math.max(0, availableAmount - amount)}
                            className="font-display text-lg font-extrabold text-foreground"
                          />
                        </div>
                      </>
                    )}
                  </div>

                  <button
                    type="button"
                    onClick={onClose}
                    className="mt-5 w-full rounded-full bg-brand px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-brand-dark"
                  >
                    Done
                  </button>
                </section>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}