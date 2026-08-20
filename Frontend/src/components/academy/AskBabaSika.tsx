"use client";

import { useRef, useState } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { academyContent, type AskEntry } from "@/lib/academyContent";
import type { Language } from "@/lib/i18n/translations";

interface ChatMessage {
  id: string;
  role: "bot" | "user";
  text: string;
}

const TYPE_CHAR_DELAY_MS = 22;
const THINKING_DELAY_MS = 550;

function findBestMatch(entries: AskEntry[], raw: string): AskEntry | null {
  const normalized = raw.toLowerCase();
  let best: AskEntry | null = null;
  let bestScore = 0;
  for (const entry of entries) {
    const score = entry.keywords.reduce((acc, keyword) => (normalized.includes(keyword) ? acc + 1 : acc), 0);
    if (score > bestScore) {
      best = entry;
      bestScore = score;
    }
  }
  return best;
}

export function AskBabaSika() {
  // Keying on language forces a full remount (and a fresh scripted greeting)
  // when it changes, instead of syncing that via an effect - it's a
  // scripted demo conversation, not a stateful backend chat.
  const { language } = useLanguage();
  return <AskBabaSikaConversation key={language} language={language} />;
}

function AskBabaSikaConversation({ language }: { language: Language }) {
  const { t } = useLanguage();
  const entries = academyContent[language].ask;

  const [messages, setMessages] = useState<ChatMessage[]>(() => [
    { id: "greeting", role: "bot", text: t("academy.ask.greeting") },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const typingTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const idCounter = useRef(0);
  const nextId = () => {
    idCounter.current += 1;
    return idCounter.current;
  };

  function respondTo(questionText: string, entry: AskEntry | null) {
    const userMessage: ChatMessage = { id: `u-${nextId()}`, role: "user", text: questionText };
    setMessages((prev) => [...prev, userMessage]);
    setIsThinking(true);

    setTimeout(() => {
      const answer = entry ? entry.answer : t("academy.ask.fallback");
      setMessages((prev) => [...prev, { id: `b-${nextId()}`, role: "bot", text: answer }]);
      setIsThinking(false);
    }, THINKING_DELAY_MS);
  }

  function handleChipClick(entry: AskEntry) {
    if (isTyping || isThinking) return;
    setIsTyping(true);
    setInputValue("");

    let index = 0;
    const typeNextChar = () => {
      index += 1;
      setInputValue(entry.question.slice(0, index));
      if (index < entry.question.length) {
        typingTimer.current = setTimeout(typeNextChar, TYPE_CHAR_DELAY_MS);
      } else {
        typingTimer.current = setTimeout(() => {
          setIsTyping(false);
          setInputValue("");
          respondTo(entry.question, entry);
        }, 200);
      }
    };
    typeNextChar();
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed || isTyping || isThinking) return;
    setInputValue("");
    respondTo(trimmed, findBestMatch(entries, trimmed));
  }

  return (
    <div className="rounded-2xl border border-border bg-surface p-6">
      <div className="flex items-center gap-3">
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand text-lg">🤖</span>
        <div>
          <h3 className="font-semibold">{t("academy.ask.title")}</h3>
          <p className="text-xs text-muted">{t("academy.ask.subtitle")}</p>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm ${
              message.role === "bot"
                ? "bg-accent-light text-foreground"
                : "ml-auto bg-brand text-white"
            }`}
          >
            {message.text}
          </div>
        ))}
        {isThinking ? (
          <div className="max-w-[65%] rounded-xl bg-accent-light px-4 py-2.5 text-sm text-muted">
            {t("academy.ask.thinking")}
          </div>
        ) : null}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {entries.map((entry) => (
          <button
            key={entry.id}
            type="button"
            onClick={() => handleChipClick(entry)}
            disabled={isTyping || isThinking}
            className="rounded-full border border-accent bg-accent-light px-3 py-1.5 text-xs font-medium text-accent-dark transition-opacity hover:opacity-80 disabled:opacity-50"
          >
            {entry.question}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="mt-4 flex items-center gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          placeholder={t("academy.ask.placeholder")}
          readOnly={isTyping}
          className="w-full flex-1 rounded-full border border-border bg-background px-4 py-2 text-sm outline-none focus:border-brand"
        />
        <button
          type="submit"
          disabled={isTyping || isThinking || !inputValue.trim()}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand text-white transition-opacity disabled:opacity-40"
          aria-label="Send"
        >
          ➤
        </button>
      </form>
    </div>
  );
}
