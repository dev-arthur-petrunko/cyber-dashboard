"use client";

import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useTranslation } from "@/components/LanguageContext";

const VERSION = "v1.1.0";

const V1_1_ITEMS = [
  "Виправлено збір даних: URLhaus (новий формат API) та Exploit-DB (date_added + вікно 60 днів)",
  "Шапка: «Допомога на розвиток проєкту», «Оновлення» та «Джерела» — окремі сторінки в одній панелі",
  "Нова сторінка «Допомога на розвиток проєкту»",
  "Сторінка «Оновлення» з історією версій",
  "Перемикач мови: абревіатури UA / EN / PL / FR / DE + яскравіший акцент",
  "Мова, Refresh та тема — в одній компактній панелі (іконки)",
  "Шапка в один рядок — одна смуга без переносів",
  "«Останні загрози»: пагінація по 10 та скрол списку",
  "Власна оцінка ризику (0–10) за методологією CVSS там, де міжнародний бал недоступний (у колонці CVSS позначається *)",
  "Vendor визначається з заголовка новинних записів, якщо джерело його не надало (позначається *)",
];

const HISTORY = [
  {
    version: "v1.0.0",
    items: [
      "18 джерел загроз (Україна + Світ)",
      "Єдина модель Threat з дедуплікацією",
      "Оцінка ризику: CVSS + EPSS + exploit maturity",
      "Cyber Timeline: публікація → PoC → KEV",
      "AI-пояснення та рекомендації для кожної загрози",
      "Дашборд на Next.js з темами та 5 мовами",
      "Автозбір даних щогодини (GitHub Actions)",
      "Telegram-розсилка через n8n + AI-агент",
      "Деплой: Render · Neon · Vercel",
    ],
  },
];

export default function UpdatesPage() {
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
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="font-mono text-xl font-black tracking-tight text-text-primary sm:text-2xl">Оновлення</h1>
            <span className="rounded-full bg-signal/10 px-2.5 py-1 font-mono text-xs font-bold text-signal">
              {VERSION}
            </span>
          </div>
          <p className="mt-2 text-xs text-text-secondary sm:text-sm">Що змінилось у поточній версії</p>
        </header>

        <section className="animate-fade-in-up" style={{ animationDelay: "100ms" }}>
          <div className="rounded-xl border border-signal/20 bg-panel p-4 shadow-sm sm:p-6">
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <h2 className="font-mono text-sm font-black tracking-tight text-text-primary sm:text-base">{VERSION}</h2>
              <span className="rounded-full bg-signal/10 px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-signal">
                Поточна
              </span>
            </div>
            <ul className="space-y-1">
              {V1_1_ITEMS.map((item) => (
                <li key={item} className="flex items-start gap-2.5 py-1 text-sm text-text-secondary">
                  <svg className="mt-0.5 h-4 w-4 flex-shrink-0 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="m5 13 4 4L19 7" />
                  </svg>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="mt-6 animate-fade-in-up" style={{ animationDelay: "200ms" }}>
          <div className="mb-4 flex items-center gap-2">
            <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-info/20 text-xs">🕘</span>
            <h2 className="text-lg font-bold text-text-primary">Історія версій</h2>
          </div>
          <div className="space-y-4">
            {HISTORY.map((entry) => (
              <div key={entry.version} className="rounded-xl border border-border bg-panel p-4 shadow-sm sm:p-6">
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <h3 className="font-mono text-sm font-black tracking-tight text-text-primary sm:text-base">{entry.version}</h3>
                  <span className="rounded-full bg-text-muted/10 px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-text-muted">
                    Попередня
                  </span>
                </div>
                <ul className="space-y-1">
                  {entry.items.map((item) => (
                    <li key={item} className="flex items-start gap-2.5 py-1 text-sm text-text-secondary">
                      <svg className="mt-0.5 h-4 w-4 flex-shrink-0 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="m5 13 4 4L19 7" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        <footer className="mt-10 animate-fade-in text-center text-xs text-text-muted" style={{ animationDelay: "300ms" }}>
          {t.sources.footer}
        </footer>
      </div>
    </main>
  );
}
