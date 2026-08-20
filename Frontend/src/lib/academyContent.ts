import type { Language } from "./i18n/translations";

export interface AcademyModule {
  id: string;
  title: string;
  subtitle: string;
  body: string;
}

export interface AskEntry {
  id: string;
  question: string;
  keywords: string[];
  answer: string;
}

interface AcademyContentSet {
  basics: AcademyModule[];
  growth: AcademyModule[];
  split: AcademyModule[];
  ask: AskEntry[];
}

// Content is deliberately accurate to what the real backend does today: no
// withdrawal lock on the emergency fund (unlike earlier BabaSika prototypes),
// mocked bank/PFA providers, PIN-confirmed contributions only.
export const academyContent: Record<Language, AcademyContentSet> = {
  en: {
    basics: [
      {
        id: "what-is-pension",
        title: "What is a pension?",
        subtitle: "Why informal workers need a savings plan",
        body: "A pension is money you set aside now so that when you stop working, you still have income to live on. Most informal workers in Nigeria don't have one — BabaSika makes starting easy, right from WhatsApp.",
      },
      {
        id: "what-is-rsa-pfa",
        title: "What is an RSA & PFA?",
        subtitle: "Retirement Savings Account & Pension Managers",
        body: "Your RSA (Retirement Savings Account) is held by a licensed Pension Fund Administrator (PFA) — a company regulated by PenCom. BabaSika registers you with a PFA you choose, and your retirement contributions build up there.",
      },
    ],
    growth: [
      {
        id: "compound-growth",
        title: "Compound growth",
        subtitle: "How regular small savings multiply",
        body: "Compound growth means your money earns on what it already earned. Small, regular contributions add up faster than you'd expect — try the estimator below.",
      },
      {
        id: "small-adds-up",
        title: "Small small adds up",
        subtitle: "Why consistency beats one big deposit",
        body: "Saving ₦200 every day beats trying to save ₦50,000 once. BabaSika is built around small, frequent contributions that fit how informal income actually arrives.",
      },
    ],
    split: [
      {
        id: "why-40-60",
        title: "Why the 40/60 split?",
        subtitle: "Balancing today's safety with tomorrow's security",
        body: "Every contribution you confirm is automatically split: 40% goes to your Emergency fund, available whenever you need it. 60% goes to your Retirement fund, registered with your PFA for the long term.",
      },
      {
        id: "what-happens-each-half",
        title: "What happens to each half?",
        subtitle: "Emergency fund vs. retirement fund",
        body: "Your Emergency fund stays with your BabaSika savings account — no lock, no waiting period, withdraw when life happens. Your Retirement fund is remitted toward your chosen PFA and grows toward your pension.",
      },
    ],
    ask: [
      {
        id: "what-is-babasika",
        question: "What is BabaSika?",
        keywords: ["what", "babasika", "about"],
        answer: "BabaSika helps Nigerian informal workers build a pension habit, right inside WhatsApp — no forms, no app to download.",
      },
      {
        id: "how-start",
        question: "How do I start?",
        keywords: ["start", "begin", "sign up", "join"],
        answer: "Message BabaSika on WhatsApp, tell us what you do for work, and we'll set up your savings account and pension registration in a few minutes.",
      },
      {
        id: "whats-4060",
        question: "What's the 40/60 split?",
        keywords: ["40", "60", "split", "forty", "sixty"],
        answer: "Every contribution you approve is split automatically: 40% to your Emergency fund (available anytime), 60% to your Retirement fund (registered with your PFA).",
      },
      {
        id: "withdraw-emergency",
        question: "Can I withdraw my emergency money anytime?",
        keywords: ["withdraw", "take out", "touch", "emergency money", "access"],
        answer: "Yes — your Emergency fund has no lock. Only your Retirement fund is registered long-term with your PFA.",
      },
      {
        id: "numbers-mean",
        question: "What do my numbers mean?",
        keywords: ["numbers", "mean", "dashboard", "balance", "score"],
        answer: "Your dashboard shows your Emergency and Retirement balances, your retirement readiness score, and your PFA registration status — all pulled live from your real BabaSika account.",
      },
      {
        id: "money-safe",
        question: "Is my money safe?",
        keywords: ["safe", "security", "secure", "trust", "risk"],
        answer: "Your savings account sits with our banking partner, and nothing ever moves without you approving the amount and confirming with your PIN on WhatsApp.",
      },
      {
        id: "fees",
        question: "Does BabaSika charge fees?",
        keywords: ["fee", "fees", "charge", "cost", "price"],
        answer: "This build doesn't charge you anything directly — it's a demo of the full experience. Any real fees would always be shown clearly before you confirm a contribution.",
      },
      {
        id: "change-job",
        question: "What if I change jobs?",
        keywords: ["job", "work", "change", "employer", "trade"],
        answer: "Nothing changes — BabaSika isn't tied to one employer or trade. Keep messaging on WhatsApp whenever you get paid, however you earn it.",
      },
    ],
  },
  pcm: {
    basics: [
      {
        id: "what-is-pension",
        title: "Wetin be pension?",
        subtitle: "Why hustle people need savings plan",
        body: "Pension na money wey you dey put aside now so that when you no dey work again, you still get money to take care of yourself. Most hustle people for Nigeria no get one — BabaSika dey make e easy to start, straight from WhatsApp.",
      },
      {
        id: "what-is-rsa-pfa",
        title: "Wetin be RSA & PFA?",
        subtitle: "Retirement Savings Account & Pension Managers",
        body: "Your RSA (Retirement Savings Account) na your special pension account where your retirement money dey grow safely with your PFA — a company wey PenCom dey regulate. BabaSika go register you with PFA wey you choose.",
      },
    ],
    growth: [
      {
        id: "compound-growth",
        title: "Compound growth",
        subtitle: "How small small savings dey multiply",
        body: "Compound growth mean say your money dey born pikin! Gain dey make gain as time dey go. Small, regular savings dey add up pass wetin you go expect — try the estimator wey dey below.",
      },
      {
        id: "small-adds-up",
        title: "Small small e dey add up",
        subtitle: "Why consistency pass one big deposit",
        body: "To save ₦200 every day pass to try save ₦50,000 one time. BabaSika dey built around small, regular savings wey fit how hustle money dey enter.",
      },
    ],
    split: [
      {
        id: "why-40-60",
        title: "Why 40/60 dey important?",
        subtitle: "Balancing today safety with tomorrow security",
        body: "Every contribution wey you confirm, e dey split automatic: 40% dey go your Emergency money, wey you fit touch anytime you need am. 60% dey go your Retirement money, wey don register with your PFA for long term.",
      },
      {
        id: "what-happens-each-half",
        title: "Wetin happen to each half?",
        subtitle: "Emergency money vs. retirement money",
        body: "Your Emergency money dey stay with your BabaSika savings account — no lock, no wait time, you fit withdraw when wahala show face. Your Retirement money dey go your chosen PFA, e dey grow toward your pension.",
      },
    ],
    ask: [
      {
        id: "what-is-babasika",
        question: "Wetin be BabaSika?",
        keywords: ["wetin", "babasika", "be"],
        answer: "BabaSika dey help Nigerian hustle people build pension habit, right inside WhatsApp — no form, no app to download.",
      },
      {
        id: "how-start",
        question: "How I go start?",
        keywords: ["start", "begin", "join", "sign"],
        answer: "Message BabaSika for WhatsApp, tell us wetin you dey do for work, we go set up your savings account and pension registration for few minutes.",
      },
      {
        id: "whats-4060",
        question: "Wetin be di 40/60 split?",
        keywords: ["40", "60", "split", "pinpin"],
        answer: "Every contribution wey you approve, e dey split automatic: 40% go your Emergency money (you fit touch am anytime), 60% go your Retirement money (e don register with your PFA).",
      },
      {
        id: "withdraw-emergency",
        question: "I fit comot my emergency money anytime?",
        keywords: ["comot", "withdraw", "touch", "emergency"],
        answer: "Yes — your Emergency money no get lock. Na only your Retirement money dem register long-term with your PFA.",
      },
      {
        id: "numbers-mean",
        question: "Wetin my numbers mean?",
        keywords: ["numbers", "mean", "dashboard", "balance", "score"],
        answer: "Your dashboard dey show your Emergency and Retirement balance, how your future readiness be, and your PFA registration status — everything come from your real BabaSika account.",
      },
      {
        id: "money-safe",
        question: "My money dey safe?",
        keywords: ["safe", "security", "trust", "risk"],
        answer: "Your savings account dey sit with our banking partner, nothing go move unless say you approve the amount and confirm with your PIN for WhatsApp.",
      },
      {
        id: "fees",
        question: "Una dey charge fees?",
        keywords: ["fee", "fees", "charge", "cost", "price"],
        answer: "This build no dey charge you anything direct — na demo of the full experience be dis. Any real fees go always show clear before you confirm any contribution.",
      },
      {
        id: "change-job",
        question: "Wetin go happen if I change work?",
        keywords: ["job", "work", "change", "employer"],
        answer: "Nothing go change — BabaSika no dey tied to one employer or trade. Just continue to message for WhatsApp anytime you chop pay, however you dey hustle am.",
      },
    ],
  },
};
