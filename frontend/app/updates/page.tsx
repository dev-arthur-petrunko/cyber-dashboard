"use client";

import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useTranslation } from "@/components/LanguageContext";

const VERSION = "v1.2.0";

const VERSION_GROUPS: { key: string; version: string; itemsKey: "v1_2" | "v1_1" | "v1_0" }[] = [
  { key: "current", version: VERSION, itemsKey: "v1_2" },
  { key: "v1.1.0", version: "v1.1.0", itemsKey: "v1_1" },
  { key: "v1.0.0", version: "v1.0.0", itemsKey: "v1_0" },
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
            <h1 className="font-mono text-xl font-black tracking-tight text-text-primary sm:text-2xl">{t.updates.title}</h1>
            <span className="rounded-full bg-signal/10 px-2.5 py-1 font-mono text-xs font-bold text-signal">
              {VERSION}
            </span>
          </div>
          <p className="mt-2 text-xs text-text-secondary sm:text-sm">{t.updates.subtitle}</p>
        </header>

        {VERSION_GROUPS.map((group) => (
          <section
            key={group.key}
            className={group.key === "current" ? "animate-fade-in-up" : "mt-6 animate-fade-in-up"}
            style={{ animationDelay: group.key === "current" ? "100ms" : "200ms" }}
          >
            <div className={group.key === "current" ? "rounded-xl border border-signal/20 bg-panel p-4 shadow-sm sm:p-6" : "mb-4"}>
              {group.key === "current" ? (
                <>
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <h2 className="font-mono text-sm font-black tracking-tight text-text-primary sm:text-base">{group.version}</h2>
                    <span className="rounded-full bg-signal/10 px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-signal">
                      {t.updates.current}
                    </span>
                  </div>
                  <ul className="space-y-1">
                    {t.updates[group.itemsKey].map((item) => (
                      <li key={item} className="flex items-start gap-2.5 py-1 text-sm text-text-secondary">
                        <svg className="mt-0.5 h-4 w-4 flex-shrink-0 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="m5 13 4 4L19 7" />
                        </svg>
                        {item}
                      </li>
                    ))}
                  </ul>
                </>
              ) : (
                <div>
                  {group.key === "v1.1.0" && (
                    <div className="mb-4 flex items-center gap-2">
                      <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-info/20 text-xs">🕘</span>
                      <h2 className="text-lg font-bold text-text-primary">{t.updates.historyTitle}</h2>
                    </div>
                  )}
                  <div className="rounded-xl border border-border bg-panel p-4 shadow-sm sm:p-6">
                    <div className="mb-3 flex flex-wrap items-center gap-2">
                      <h3 className="font-mono text-sm font-black tracking-tight text-text-primary sm:text-base">{group.version}</h3>
                      <span className="rounded-full bg-text-muted/10 px-2 py-0.5 font-mono text-[10px] font-bold uppercase text-text-muted">
                        {t.updates.previous}
                      </span>
                    </div>
                    <ul className="space-y-1">
                      {t.updates[group.itemsKey].map((item) => (
                        <li key={item} className="flex items-start gap-2.5 py-1 text-sm text-text-secondary">
                          <svg className="mt-0.5 h-4 w-4 flex-shrink-0 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="m5 13 4 4L19 7" />
                          </svg>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </section>
        ))}

        <footer className="mt-10 animate-fade-in text-center text-xs text-text-muted" style={{ animationDelay: "300ms" }}>
          {t.sources.footer}
        </footer>
      </div>
    </main>
  );
}
