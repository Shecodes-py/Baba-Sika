"use client";

import { useState } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { getAcademyContent } from "@/lib/academyContent";
import type { TranslationKey } from "@/lib/i18n/translations";
import { ModuleCard } from "./ModuleCard";
import { SavingsEstimator } from "./SavingsEstimator";

const TABS: { id: "basics" | "growth" | "split"; labelKey: TranslationKey }[] = [
  { id: "basics", labelKey: "academy.tab.basics" },
  { id: "growth", labelKey: "academy.tab.growth" },
  { id: "split", labelKey: "academy.tab.split" },
];

export function ModuleTabs() {
  const { t, language } = useLanguage();
  const [activeTab, setActiveTab] = useState<"basics" | "growth" | "split">("basics");
  const modules = getAcademyContent(language)[activeTab];

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            aria-pressed={activeTab === tab.id}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors ${
              activeTab === tab.id
                ? "bg-brand text-white"
                : "border border-border bg-surface text-muted hover:text-foreground"
            }`}
          >
            {t(tab.labelKey)}
          </button>
        ))}
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        {modules.map((moduleTopic) => (
          <ModuleCard key={moduleTopic.id} moduleTopic={moduleTopic} />
        ))}
      </div>

      {activeTab === "growth" ? (
        <div className="mt-4">
          <SavingsEstimator />
        </div>
      ) : null}
    </div>
  );
}
