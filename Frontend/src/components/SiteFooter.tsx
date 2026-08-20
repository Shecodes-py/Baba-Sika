"use client";

import { useLanguage } from "@/lib/i18n/LanguageContext";

export function SiteFooter() {
  const { t } = useLanguage();
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border bg-surface">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-2 px-6 py-8 text-center text-sm text-muted">
        <p className="font-medium text-foreground">BabaSika — {t("footer.tagline")}</p>
        <p>
          © {year} BabaSika. {t("footer.rights")}
        </p>
      </div>
    </footer>
  );
}
