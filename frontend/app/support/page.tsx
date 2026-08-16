"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useTranslation } from "@/components/LanguageContext";

export default function SupportPage() {
  const router = useRouter();
  const { t } = useTranslation();
  const [showCard, setShowCard] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText("4874 1000 3975 4612");
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

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
            <p className="mt-3 text-sm leading-relaxed text-text-secondary">{t.support.p3}</p>
            <p className="mt-3 text-sm leading-relaxed text-text-secondary">{t.support.thanks}</p>
          </div>
        </section>

        <section className="animate-fade-in-up mt-4" style={{ animationDelay: "200ms" }}>
          <div className="rounded-xl border border-signal/20 bg-signal/5 p-4 shadow-sm sm:p-6">
            <div className="mb-3 flex flex-wrap items-center gap-x-3 gap-y-2">
              <h2 className="flex items-center gap-2 text-lg font-bold text-text-primary">
                <span>💙</span>
                {t.support.donateTitle}
              </h2>
              <span className="inline-flex items-center gap-1.5 rounded-full border border-signal/30 bg-signal/10 px-3 py-1 text-xs font-bold text-signal">
                🎯 {t.support.goal}
              </span>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <a
                href="https://ko-fi.com/arthurpetrunko"
                target="_blank"
                rel="noreferrer"
                className="group inline-flex items-center justify-between gap-2 rounded-xl border border-border bg-panel p-4 shadow-sm transition-all hover:-translate-y-0.5 hover:border-signal/40 hover:shadow-md"
              >
                <span className="flex items-center gap-2 text-sm font-semibold text-text-primary">
                  <span className="text-lg">☕</span>
                  {t.support.koFi}
                </span>
                <svg className="h-4 w-4 text-text-muted transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 5l7 7-7 7M5 12h15" />
                </svg>
              </a>

              <a
                href="https://send.monobank.ua/jar/A55e1mCwVQ"
                target="_blank"
                rel="noreferrer"
                className="group inline-flex items-center justify-between gap-2 rounded-xl border border-border bg-panel p-4 shadow-sm transition-all hover:-translate-y-0.5 hover:border-signal/40 hover:shadow-md"
              >
                <span className="flex items-center gap-2 text-sm font-semibold text-text-primary">
                  <span className="text-lg">🏦</span>
                  {t.support.monobank}
                </span>
                <svg className="h-4 w-4 text-text-muted transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 5l7 7-7 7M5 12h15" />
                </svg>
              </a>
            </div>

            <div className="mt-3 rounded-xl border border-border bg-panel-raised/60 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-text-muted sm:text-sm">
                  {t.support.cardLabel}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowCard(!showCard)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-panel px-3 py-1.5 text-xs font-medium text-text-secondary shadow-sm transition-all hover:border-signal/40 hover:text-signal"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      {showCard ? (
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                      )}
                    </svg>
                    {showCard ? t.support.hideCard : t.support.showCard}
                  </button>
                  <button
                    type="button"
                    onClick={handleCopy}
                    disabled={!showCard}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-panel px-3 py-1.5 text-xs font-medium text-text-secondary shadow-sm transition-all hover:border-signal/40 hover:text-signal disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 01-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 011.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 00-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 01-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 00-3.375-3.375h-1.5a1.125 1.125 0 01-1.125-1.125v-1.5a3.375 3.375 0 00-3.375-3.375H9.75" />
                    </svg>
                    {copied ? t.support.copied : t.support.copy}
                  </button>
                </div>
              </div>
              <div className="mt-3 min-h-10">
                {showCard ? (
                  <div className="animate-fade-in inline-flex items-center gap-2 rounded-lg border border-border bg-panel px-4 py-2 font-mono text-base font-bold tracking-[0.15em] text-text-primary sm:text-lg">
                    <svg className="h-4 w-4 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <rect x="3" y="5" width="18" height="14" rx="2" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 10h18" />
                    </svg>
                    4874 1000 3975 4612
                  </div>
                ) : (
                  <div className="animate-fade-in inline-flex items-center gap-2 rounded-lg border border-dashed border-border bg-panel px-4 py-2 font-mono text-base font-bold tracking-[0.15em] text-text-muted/50 sm:text-lg">
                    •••• •••• •••• ••••
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        <footer className="mt-10 animate-fade-in text-center text-xs text-text-muted" style={{ animationDelay: "300ms" }}>
          {t.sources.footer}
        </footer>
      </div>
    </main>
  );
}
