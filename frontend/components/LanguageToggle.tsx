"use client";

import { useTranslation } from "./LanguageContext";

export function LanguageToggle() {
  const { lang, setLang, t } = useTranslation();

  const toggle = () => {
    setLang(lang === "uk" ? "en" : "uk");
  };

  return (
    <button
      onClick={toggle}
      className="group relative flex h-7 items-center gap-1 rounded-lg border border-border bg-panel px-2 hover:bg-panel-raised transition-all sm:h-9 sm:gap-1.5 sm:px-3"
      aria-label={lang === "uk" ? "Switch to English" : "Переключити на українську"}
    >
      <span className={`text-xs font-bold transition-colors sm:text-sm ${lang === "uk" ? "text-ua-blue" : "text-text-muted"}`}>
        UK
      </span>
      <span className="h-3 w-px bg-border sm:h-4" />
      <span className={`text-xs font-bold transition-colors sm:text-sm ${lang === "en" ? "text-signal" : "text-text-muted"}`}>
        EN
      </span>
    </button>
  );
}
