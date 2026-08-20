"use client";

import { useRef, useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { DemoControls } from "@/components/dashboard/DemoControls";
import { demoBankAccount, demoContributions, demoProgress } from "@/lib/demoData";
import { contributionsToActivityEntries, type ActivityEntry } from "@/lib/activity";

const EMERGENCY_RATIO = Number.parseFloat(demoProgress.emergency_ratio); // 0.40
const SALE_MIN = 150;
const SALE_MAX = 600;
const WITHDRAW_MIN = 100;
const WITHDRAW_MAX = 300;

function randomBetween(min: number, max: number): number {
  return Math.round(min + Math.random() * (max - min));
}

export function DemoDashboardClient() {
  // A "sale" moves money OUT of the bank balance and INTO the two BabaSika
  // buckets (split 40/60), same direction as a real confirmed contribution -
  // a "withdrawal" moves the emergency portion back into the bank balance.
  const [bankBalance, setBankBalance] = useState(() => Number.parseFloat(demoBankAccount.last_known_balance ?? "0"));
  const [emergencyBalance, setEmergencyBalance] = useState(() =>
    Number.parseFloat(demoProgress.emergency_fund_balance),
  );
  const [retirementBalance, setRetirementBalance] = useState(() =>
    Number.parseFloat(demoProgress.retirement_balance),
  );
  const [entries, setEntries] = useState<ActivityEntry[]>(() => contributionsToActivityEntries(demoContributions));
  const idCounter = useRef(1000);
  const nextId = () => {
    idCounter.current += 1;
    return String(idCounter.current);
  };

  function handleSimulateSale() {
    const saleAmount = randomBetween(SALE_MIN, SALE_MAX);
    const emergencyCut = Math.round(saleAmount * EMERGENCY_RATIO);
    const retirementCut = saleAmount - emergencyCut;
    const now = new Date().toISOString();

    setBankBalance((prev) => prev + saleAmount);
    setEmergencyBalance((prev) => prev + emergencyCut);
    setRetirementBalance((prev) => prev + retirementCut);
    setEntries((prev) => [
      { id: nextId(), kind: "emergency_fund", amount: emergencyCut.toFixed(2), occurredAt: now },
      { id: nextId(), kind: "retirement_fund", amount: retirementCut.toFixed(2), occurredAt: now },
      ...prev,
    ]);
  }

  function handleWithdraw() {
    if (emergencyBalance <= 0) return;
    const amount = Math.min(emergencyBalance, randomBetween(WITHDRAW_MIN, WITHDRAW_MAX));
    setEmergencyBalance((prev) => Math.max(0, prev - amount));
    setBankBalance((prev) => prev + amount);
    setEntries((prev) => [
      { id: nextId(), kind: "withdrawal", amount: amount.toFixed(2), occurredAt: new Date().toISOString() },
      ...prev,
    ]);
  }

  const progress = {
    ...demoProgress,
    emergency_fund_balance: emergencyBalance.toFixed(2),
    retirement_balance: retirementBalance.toFixed(2),
  };
  const bankAccount = { ...demoBankAccount, last_known_balance: bankBalance.toFixed(2) };

  return (
    <DashboardShell
      progress={progress}
      activityEntries={entries}
      bankAccount={bankAccount}
      isDemo
      greetingName="Iya Iyabo"
      controls={
        <DemoControls onSimulateSale={handleSimulateSale} onWithdraw={handleWithdraw} canWithdraw={emergencyBalance > 0} />
      }
    />
  );
}
