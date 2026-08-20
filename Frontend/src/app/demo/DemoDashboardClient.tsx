"use client";

import { useRef, useState } from "react";
import { DashboardShell } from "@/components/dashboard/DashboardShell";
import { DemoControls } from "@/components/dashboard/DemoControls";
import {
  MoveMoneyModal,
  type MoveMoneyMode,
  type MoveMoneyResult,
} from "@/components/dashboard/MoveMoneyModal";
import { demoProgress } from "@/lib/demoData";
import { demoTransactions, type TransactionEntry } from "@/lib/transactions";
import { formatNaira } from "@/lib/format";

const SALE_MIN = 150;
const SALE_MAX = 600;
const WITHDRAW_MIN = 100;
const WITHDRAW_MAX = 300;

function randomBetween(min: number, max: number): number {
  return Math.round(min + Math.random() * (max - min));
}

export function DemoDashboardClient() {
  const [bankBalance, setBankBalance] = useState(() =>
    Number.parseFloat(demoProgress.bank_account_balance ?? "0"),
  );
  const [emergencyBalance, setEmergencyBalance] = useState(() =>
    Number.parseFloat(demoProgress.emergency_fund_balance),
  );
  const [retirementBalance, setRetirementBalance] = useState(() =>
    Number.parseFloat(demoProgress.retirement_balance),
  );
  const [transactions, setTransactions] = useState<TransactionEntry[]>(demoTransactions);
  const [modal, setModal] = useState<{ mode: MoveMoneyMode } | null>(null);
  const idCounter = useRef(1000);
  const nextId = () => {
    idCounter.current += 1;
    return String(idCounter.current);
  };

  function handleComplete(result: MoveMoneyResult) {
    const now = new Date().toISOString();
    if (result.kind === "sale") {
      setBankBalance((prev) => Math.max(0, prev - result.amount));
      setEmergencyBalance((prev) => prev + result.emergencyCut);
      setRetirementBalance((prev) => prev + result.retirementCut);
      setTransactions((prev) => [
        {
          id: nextId(),
          kind: "market_sale",
          title: "Market sale contribution",
          subtext: `${formatNaira(result.emergencyCut)} Contingent · ${formatNaira(result.retirementCut)} Retirement`,
          total: result.amount,
          contingency: result.emergencyCut,
          retirement: result.retirementCut,
          status: "success",
          occurredAt: now,
        },
        ...prev,
      ]);
    } else {
      setEmergencyBalance((prev) => Math.max(0, prev - result.amount));
      setTransactions((prev) => [
        {
          id: nextId(),
          kind: "withdrawal",
          title: "Emergency withdrawal",
          subtext: `${formatNaira(result.amount)} withdrawn from Contingent (Safety)`,
          total: result.amount,
          contingency: 0,
          retirement: 0,
          status: "success",
          occurredAt: now,
        },
        ...prev,
      ]);
    }
  }

  function openModal(mode: MoveMoneyMode) {
    setModal({ mode });
  }

  const available =
    modal?.mode === "withdrawal" ? emergencyBalance : modal?.mode === "sale" ? bankBalance : 0;

  const modalInitial =
    modal?.mode === "sale"
      ? randomBetween(SALE_MIN, SALE_MAX)
      : Math.min(randomBetween(WITHDRAW_MIN, WITHDRAW_MAX), emergencyBalance);

  const progress = {
    ...demoProgress,
    bank_account_balance: bankBalance.toFixed(2),
    emergency_fund_balance: emergencyBalance.toFixed(2),
    retirement_balance: retirementBalance.toFixed(2),
  };

  return (
    <>
      <DashboardShell
        progress={progress}
        transactions={transactions}
        isDemo
        greetingName="Iya Iyabo"
        controls={
          <DemoControls
            onSimulateSale={() => openModal("sale")}
            onWithdraw={() => {
              if (emergencyBalance > 0) openModal("withdrawal");
            }}
            canWithdraw={emergencyBalance > 0}
          />
        }
      />
      {modal && (
        <MoveMoneyModal
          key={modal.mode}
          mode={modal.mode}
          initialAmount={modalInitial}
          availableAmount={available}
          available={{ bank: bankBalance, emergency: emergencyBalance, retirement: retirementBalance }}
          onComplete={handleComplete}
          onClose={() => setModal(null)}
        />
      )}
    </>
  );
}