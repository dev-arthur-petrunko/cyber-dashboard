"use client";

import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useTranslation } from "@/components/LanguageContext";

export default function SupportPage() {
  const router = useRouter();
  const { t } = useTranslation();

  return (
    <main className="min-h-screen bg-bg">
      <div className="mx-auto max-w-5xl px-3 py-4 sm:px-4 sm:py-6 lg:px-8 lg:py-8">
        <div className="mb-6 flex items-center justify-between">
          <button
            onClick={() => router.push("/")}
            className="inline-flex items-center gap-2 rounded-lg border border-border bg-panel px-4 py-2 text-sm font-medium text-text-secondary shadow-sm transition-all hover:border-signal/40 hover:text-signal"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            {t.sources.backToDashboard}
          </button>
          <div className="flex items-center gap-2">
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </div>

        <header className="mb-6 animate-fade-in-up sm:mb-8">
          <h1 className="font-mono text-xl font-black tracking-tight text-text-primary sm:text-2xl">
            {t.support.title}
          </h1>
          <p className="mt-2 text-xs text-text-secondary sm:text-sm">
            {t.support.subtitle}
          </p>
        </header>

        <section className="animate-fade-in-up" style={{ animationDelay: "100ms" }}>
          <div className="rounded-xl border border-border bg-panel p-4 shadow-sm sm:p-6">
            <p className="text-sm leading-relaxed text-text-secondary">{t.support.p1}</p>
            <p className="mt-3 text-sm leading-relaxed text-text-secondary">{t.support.p2}</p>
            <p className="mt-3 text-sm leading-relaxed text-text-secondary">{t.support.thanks}</p>
          </div>
        </section>

        <section className="animate-fade-in-up mt-4" style={{ animationDelay: "200ms" }}>
          <div className="rounded-xl border border-signal/20 bg-signal/5 p-4 shadow-sm sm:p-6">
            <div className="mb-3 flex items-center gap-2">
              <span className="text-lg">💙</span>
              <h2 className="text-lg font-bold text-text-primary">{t.support.donateTitle}</h2>
            </div>
            <p className="text-sm text-text-secondary">{t.support.donateText}</p>
          </div>
        </section>

        <footer className="mt-10 animate-fade-in text-center text-xs text-text-muted" style={{ animationDelay: "300ms" }}>
          {t.sources.footer}
        </footer>
      </div>
    </main>
  );
}
