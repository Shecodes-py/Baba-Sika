"use client";

import { useReducer } from "react";
import { motion } from "framer-motion";
import { demoProgress } from "@/lib/demoData";
import { formatNaira } from "@/lib/format";

const USSD_CODE = "*347#";
const EMERGENCY_RATIO = Number.parseFloat(demoProgress.emergency_ratio);

type Screen =
  | { name: "dial"; buffer: string; error?: boolean }
  | { name: "menu" }
  | { name: "balance" }
  | { name: "pfa" }
  | { name: "saveAmount"; buffer: string; error?: boolean }
  | { name: "saveConfirm"; amount: number }
  | { name: "savePin"; amount: number; buffer: string; error?: boolean }
  | { name: "saveSuccess"; amount: number }
  | { name: "income" }
  | { name: "incomeAmount"; buffer: string; error?: boolean }
  | { name: "incomeSuccess"; amount: number }
  | { name: "exit" };

interface UssdState {
  screen: Screen;
  bank: number;
  emergency: number;
  retirement: number;
}

const initialState: UssdState = {
  screen: { name: "dial", buffer: "" },
  bank: Number.parseFloat(demoProgress.bank_account_balance ?? "0"),
  emergency: Number.parseFloat(demoProgress.emergency_fund_balance),
  retirement: Number.parseFloat(demoProgress.retirement_balance),
};

const DIGITS = new Set(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "#"]);

type UssdAction =
  | { type: "key"; key: string }
  | { type: "send" }
  | { type: "back" };

function goToMenu(state: UssdState): UssdState {
  return { ...state, screen: { name: "menu" } };
}

function reducer(state: UssdState, action: UssdAction): UssdState {
  const { screen } = state;

  switch (action.type) {
    case "key": {
      if (action.key === "C") return { ...state, screen: { name: "dial", buffer: "" } };
      if (!DIGITS.has(action.key)) return state;

      switch (screen.name) {
        case "dial":
          if (screen.buffer.length >= 10) return state;
          return { ...state, screen: { name: "dial", buffer: screen.buffer + action.key, error: false } };
        case "menu":
          switch (action.key) {
            case "1": return { ...state, screen: { name: "balance" } };
            case "2": return { ...state, screen: { name: "saveAmount", buffer: "" } };
            case "3": return { ...state, screen: { name: "income" } };
            case "4": return { ...state, screen: { name: "pfa" } };
            case "0": return { ...state, screen: { name: "exit" } };
            default: return state;
          }
        case "balance":
        case "pfa":
        case "saveSuccess":
        case "incomeSuccess":
          return goToMenu(state);
        case "saveAmount":
        case "incomeAmount":
          if (action.key === "*" || action.key === "#") return state;
          if (screen.buffer.length >= 7) return state;
          return { ...state, screen: { ...screen, buffer: screen.buffer + action.key, error: false } };
        case "saveConfirm":
          if (action.key === "1") return { ...state, screen: { name: "savePin", amount: screen.amount, buffer: "" } };
          if (action.key === "2") return { ...state, screen: { name: "saveAmount", buffer: "" } };
          return state;
        case "savePin":
          if (action.key === "*" || action.key === "#") return state;
          if (screen.buffer.length >= 4) return state;
          return { ...state, screen: { ...screen, buffer: screen.buffer + action.key, error: false } };
        case "income":
          if (action.key === "1") return { ...state, screen: { name: "incomeSuccess", amount: 1000 } };
          if (action.key === "2") return { ...state, screen: { name: "incomeSuccess", amount: 2000 } };
          if (action.key === "3") return { ...state, screen: { name: "incomeSuccess", amount: 5000 } };
          if (action.key === "4") return { ...state, screen: { name: "incomeAmount", buffer: "" } };
          if (action.key === "0") return { ...state, screen: { name: "exit" } };
          return state;
        case "exit":
          return { ...state, screen: { name: "dial", buffer: "" } };
        default:
          return state;
      }
    }

    case "send": {
      switch (screen.name) {
        case "dial":
          if (screen.buffer === USSD_CODE) return goToMenu(state);
          return { ...state, screen: { name: "dial", buffer: "", error: true } };
        case "saveAmount":
        case "incomeAmount": {
          const amount = Number.parseInt(screen.buffer, 10);
          if (!screen.buffer || Number.isNaN(amount) || amount <= 0) {
            return { ...state, screen: { ...screen, error: true } };
          }
          if (screen.name === "incomeAmount") {
            return { ...state, screen: { name: "incomeSuccess", amount } };
          }
          return { ...state, screen: { name: "saveConfirm", amount } };
        }
        case "savePin": {
          if (screen.buffer.length !== 4) {
            return { ...state, screen: { ...screen, error: true } };
          }
          const emergencyCut = Math.round(screen.amount * EMERGENCY_RATIO);
          const retirementCut = screen.amount - emergencyCut;
          return {
            ...state,
            bank: state.bank - screen.amount,
            emergency: state.emergency + emergencyCut,
            retirement: state.retirement + retirementCut,
            screen: { name: "saveSuccess", amount: screen.amount },
          };
        }
        case "balance":
        case "pfa":
        case "saveSuccess":
        case "incomeSuccess":
        case "exit":
          return goToMenu(state);
        default:
          return state;
      }
    }

    case "back": {
      switch (screen.name) {
        case "dial":
          return { ...state, screen: { name: "dial", buffer: "" } };
        case "menu":
        case "exit":
          return { ...state, screen: { name: "dial", buffer: "" } };
        default:
          return goToMenu(state);
      }
    }
  }
}

function screenKey(screen: Screen): string {
  return screen.name === "savePin" ? `${screen.name}-${screen.amount}-${screen.buffer.length}` : screen.name;
}

function ScreenBody({ state }: { state: UssdState }) {
  const { screen } = state;
  const caret = "▌";

  switch (screen.name) {
    case "dial":
      return (
        <>
          <p>BabaSika Pension</p>
          <p className="mt-3">
            {screen.error ? "Invalid code.\nDial the BabaSika code and press Send again." : `Dial ${USSD_CODE} then press Send.`}
          </p>
          <p className="mt-4">
            &gt; {screen.buffer}
            <span className="opacity-80">{caret}</span>
          </p>
        </>
      );
    case "menu":
      return (
        <>
          <p className="font-bold text-green-300">BabaSika Pension</p>
          <p className="mt-3">
            1. Check balance
            <br />2. Save now
            <br />3. Log income
            <br />4. PFA status
            <br />0. Exit
          </p>
          <p className="mt-3 text-green-500">Reply with your choice.</p>
        </>
      );
    case "balance":
      return (
        <>
          <p className="font-bold text-green-300">BabaSika</p>
          <p className="mt-3">
            Bank: {formatNaira(state.bank)}
            <br />
            Emergency: {formatNaira(state.emergency)}
            <br />
            Retirement: {formatNaira(state.retirement)}
          </p>
          <p className="mt-3 text-green-500">Thank you. Press Send to continue.</p>
        </>
      );
    case "pfa":
      return (
        <>
          <p className="font-bold text-green-300">BabaSika</p>
          <p className="mt-3">
            PFA: Sigma Pensions
            <br />
            Status: Registered
            <br />
            RSA PIN: PEN1234567890
          </p>
          <p className="mt-3 text-green-500">You are covered! Press Send to continue.</p>
        </>
      );
    case "saveAmount":
      return (
        <>
          <p>Enter amount to save:</p>
          <p className="mt-3 text-green-300">
            &gt; {screen.buffer}
            <span className="opacity-80">{caret}</span>
          </p>
          {screen.error && <p className="mt-3 text-red-400">Invalid amount. Try again.</p>}
        </>
      );
    case "saveConfirm": {
      const emergencyCut = Math.round(screen.amount * EMERGENCY_RATIO);
      const retirementCut = screen.amount - emergencyCut;
      return (
        <>
          <p className="font-bold text-green-300">Save {formatNaira(screen.amount)}?</p>
          <p className="mt-3">
            Emergency ({Math.round(EMERGENCY_RATIO * 100)}%): {formatNaira(emergencyCut)}
            <br />
            Retirement ({100 - Math.round(EMERGENCY_RATIO * 100)}%): {formatNaira(retirementCut)}
          </p>
          <p className="mt-3">
            1. Confirm
            <br />2. Change
          </p>
        </>
      );
    }
    case "savePin":
      return (
        <>
          <p>Enter 4-digit PIN:</p>
          <p className="mt-3 tracking-widest text-green-300">
            {screen.buffer.replace(/./g, "•")}
            <span className="opacity-80">{caret}</span>
          </p>
          {screen.error && <p className="mt-3 text-red-400">PIN must be 4 digits.</p>}
        </>
      );
    case "saveSuccess": {
      const emergencyCut = Math.round(screen.amount * EMERGENCY_RATIO);
      const retirementCut = screen.amount - emergencyCut;
      return (
        <>
          <p className="font-bold text-green-300">Saved! {formatNaira(screen.amount)} set aside.</p>
          <p className="mt-3">
            Emergency: +{formatNaira(emergencyCut)}
            <br />
            Retirement: +{formatNaira(retirementCut)}
          </p>
          <p className="mt-3 text-green-500">Small small, your future dey grow.</p>
        </>
      );
    }
    case "income":
      return (
        <>
          <p className="font-bold text-green-300">Log today&apos;s income</p>
          <p className="mt-3">
            1. {formatNaira(1000)}
            <br />2. {formatNaira(2000)}
            <br />3. {formatNaira(5000)}
            <br />4. Other
            <br />0. Exit
          </p>
        </>
      );
    case "incomeAmount":
      return (
        <>
          <p>Enter amount you earned:</p>
          <p className="mt-3 text-green-300">
            &gt; {screen.buffer}
            <span className="opacity-80">{caret}</span>
          </p>
          {screen.error && <p className="mt-3 text-red-400">Invalid amount. Try again.</p>}
        </>
      );
    case "incomeSuccess":
      return (
        <>
          <p className="font-bold text-green-300">Income logged: {formatNaira(screen.amount)}</p>
          <p className="mt-3 text-green-500">BabaSika go remind you to save later.</p>
          <p className="mt-3 text-green-500">Press Send to continue.</p>
        </>
      );
    case "exit":
      return (
        <>
          <p className="font-bold text-green-300">Session ended.</p>
          <p className="mt-3">
            Dial {USSD_CODE} anytime to save more.
            <br />
            Bye! Press Send to start again.
          </p>
        </>
      );
  }
}

const KEYPAD_ROWS = ["123", "456", "789", "*0#"];

export function UssdSimulator() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <div className="mx-auto w-[300px] rounded-[2.5rem] border-[10px] border-forest-950 bg-forest-950 shadow-2xl shadow-forest-950/40">
      <div className="flex h-[540px] flex-col overflow-hidden rounded-[2rem] bg-[#04180f]">
        <div className="flex items-center justify-between px-4 py-2 font-mono text-[10px] text-green-500/70">
          <span>BabaSika</span>
          <span>▰▰▰▰◔ 09:41</span>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-3 font-mono text-[13px] leading-6 text-green-400">
          <motion.div
            key={screenKey(state.screen)}
            initial={{ opacity: 0, y: 2 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.12 }}
          >
            <ScreenBody state={state} />
          </motion.div>
        </div>

        <div className="grid grid-cols-3 gap-2 p-3">
          {KEYPAD_ROWS.flatMap((row) => row.split("")).map((key) => (
            <button
              key={key}
              type="button"
              onClick={() => dispatch({ type: "key", key })}
              className="select-none rounded-lg bg-forest-800 py-2.5 font-mono text-base font-bold text-white transition active:scale-95 active:bg-forest-600 hover:bg-forest-700"
            >
              {key}
            </button>
          ))}
          <button
            type="button"
            onClick={() => dispatch({ type: "back" })}
            className="rounded-lg bg-forest-700 py-2.5 text-xs font-bold text-white transition active:scale-95 hover:bg-forest-600"
          >
            ◀ Back
          </button>
          <button
            type="button"
            onClick={() => dispatch({ type: "send" })}
            className="col-span-2 rounded-lg bg-amber-400 py-2.5 text-sm font-extrabold text-forest-950 transition active:scale-95 hover:bg-amber-300"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}