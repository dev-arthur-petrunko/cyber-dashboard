"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { Language, translations, Translations } from "@/lib/i18n";

type TranslationDict = Translations[Language];

const LANGS: Language[] = ["uk", "en", "pl", "fr", "de"];
const COOKIE_MAX_AGE = 31536000;

function getInitialLang(): Language {
  if (typeof window === "undefined") return "uk";
  const stored = localStorage.getItem("lang");
  if (stored && (LANGS as string[]).includes(stored)) return stored as Language;
  const match = document.cookie.match(/(?:^|;\s*)lang=([a-z]{2})/);
  if (match && (LANGS as string[]).includes(match[1])) return match[1] as Language;
  return "uk";
}

function setLangCookie(lang: Language) {
  document.cookie = `lang=${lang}; path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
}

interface LanguageContextValue {
  lang: Language;
  setLang: (lang: Language) => void;
  t: TranslationDict;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Language>(getInitialLang);

  useEffect(() => {
    const stored = localStorage.getItem("lang");
    if (stored && (LANGS as string[]).includes(stored) && stored !== lang) {
      setLangState(stored as Language);
    } else if (!document.cookie.match(/(?:^|;\s*)lang=/)) {
      setLangCookie(lang);
    }
  }, [lang]);

  const setLang = (newLang: Language) => {
    setLangState(newLang);
    localStorage.setItem("lang", newLang);
    setLangCookie(newLang);
  };

  const t = translations[lang];

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useTranslation() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useTranslation must be used within LanguageProvider");
  return ctx;
}
