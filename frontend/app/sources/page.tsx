"use client";

import { useRouter } from "next/navigation";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { useTranslation } from "@/components/LanguageContext";
import sources from "../../../data/sources_status.json";

interface SourceItem {
  name: string;
  url: string;
  status?: string;
  description?: string;
  problem?: string;
  possible_solution?: string;
  requires_key?: string | null;
  docs?: string;
}

export default function SourcesPage() {
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
          <h1 className="font-mono text-xl font-black tracking-tight text-text-primary sm:text-2xl">{t.sources.title}</h1>
          <p className="mt-2 text-xs text-text-secondary sm:text-sm">
            {t.sources.subtitle}
          </p>
        </header>

        {/* Telemetry API */}
        <SourceSection
          title={t.sources.telemetry}
          icon="🛰"
          items={(sources.telemetry_api as SourceItem[]) || []}
          render={(s, i) => (
            <TelemetryCard key={s.name} item={s} delay={i} />
          )}
        />

        {/* Vendor RSS */}
        <SourceSection
          title={t.sources.vendorRSS}
          icon="📡"
          items={(sources.vendor_rss as SourceItem[]) || []}
          render={(s, i) => (
            <SourceCard name={s.name} url={s.url} description={s.description || ""} status="active" delay={i} />
          )}
        />

        {/* Integrated UA sources */}
        <SourceSection
          title={t.sources.integrated}
          icon="✓"
          items={(sources.integrated_ua as SourceItem[]) || []}
          render={(s, i) => (
            <SourceCard name={s.name} url={s.url} description={s.description || ""} status="active" delay={i} />
          )}
        />

        {/* Planned UA sources */}
        <SourceSection
          title={t.sources.planned}
          icon="⚠"
          items={(sources.planned_ua as SourceItem[]) || []}
          render={(s, i) => (
            <PlannedCard key={s.name} item={s} delay={i} />
          )}
        />

        {/* Telegram channels */}
        <section className="animate-fade-in-up mb-8" style={{ animationDelay: "300ms" }}>
          <div className="mb-4 flex items-center gap-2">
            <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-info/20 text-xs">✈</span>
            <h2 className="text-lg font-bold text-text-primary">{t.sources.telegram}</h2>
          </div>
          <div className="rounded-xl border border-info/30 bg-info/5 p-4 text-sm text-info shadow-sm">
            <p className="mb-3">{sources.note}</p>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
            {sources.telegram_channels.map((ch, i) => (
              <a
                key={ch.name}
                href={ch.url}
                target="_blank"
                rel="noreferrer"
                className="animate-fade-in-up group flex items-center justify-between rounded-lg border border-border bg-panel p-3 shadow-sm transition-all hover:border-info/40 hover:shadow-md"
                style={{ animationDelay: `${400 + i * 80}ms` }}
              >
                <div>
                  <p className="font-medium text-text-primary transition-colors group-hover:text-info">{ch.name}</p>
                  <p className="text-xs text-text-muted">{ch.description}</p>
                </div>
                <svg className="h-4 w-4 text-text-muted transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            ))}
          </div>
        </section>

        <footer className="mt-10 animate-fade-in text-center text-xs text-text-muted" style={{ animationDelay: "500ms" }}>
          {t.sources.footer}
        </footer>
      </div>
    </main>
  );
}

function SourceSection<T extends SourceItem>({
  title,
  icon,
  items,
  render,
}: {
  title: string;
  icon: string;
  items: T[];
  render: (item: T, index: number) => React.ReactNode;
}) {
  if (!items.length) return null;
  return (
    <section className="animate-fade-in-up mb-8" style={{ animationDelay: "100ms" }}>
      <div className="mb-4 flex items-center gap-2">
        <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-signal/20 text-xs">{icon}</span>
        <h2 className="text-lg font-bold text-text-primary">{title}</h2>
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {items.map((s, i) => render(s, i))}
      </div>
    </section>
  );
}

function SourceCard({
  name,
  url,
  description,
  status,
  delay,
}: {
  name: string;
  url: string;
  description: string;
  status: "active";
  delay: number;
}) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      className="animate-fade-in-up group relative overflow-hidden rounded-xl border border-border bg-panel p-4 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-lg sm:p-5"
      style={{ animationDelay: `${150 + delay * 80}ms` }}
    >
      <div className="absolute inset-x-0 top-0 h-1 bg-signal" />
      <div className="flex items-start justify-between">
        <h3 className="font-bold text-text-primary transition-colors group-hover:text-signal">{name}</h3>
        <span className="inline-flex items-center gap-1 rounded-full bg-signal/10 px-2 py-0.5 text-[10px] font-bold uppercase text-signal">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-signal" />
          {status}
        </span>
      </div>
      <p className="mt-2 text-sm text-text-secondary">{description}</p>
      <p className="mt-3 truncate text-xs text-text-muted">{new URL(url).hostname}</p>
    </a>
  );
}

function TelemetryCard({ item, delay }: { item: SourceItem; delay: number }) {
  const { t } = useTranslation();
  const badgeColor = item.status === "active" ? "bg-signal" : item.status === "partial" ? "bg-warning" : "bg-info";
  const badgeText = item.status === "active" ? t.sources.active : item.status === "partial" ? t.sources.partial : t.sources.statusPlanned;

  return (
    <div
      className="animate-fade-in-up glass-card relative overflow-hidden rounded-xl border border-border p-4 shadow-sm sm:p-5"
      style={{ animationDelay: `${150 + delay * 80}ms` }}
    >
      <div className={`absolute inset-x-0 top-0 h-1 ${badgeColor}`} />
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-bold text-text-primary">{item.name}</h3>
        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold uppercase text-white ${badgeColor}`}>
          {badgeText}
        </span>
      </div>
      <p className="text-sm text-text-secondary">{item.description}</p>
      {item.requires_key && (
        <p className="mt-2 text-xs text-warning">
          {t.sources.keyRequired} <span className="font-mono font-semibold">{item.requires_key}</span>
        </p>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <a
          href={item.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 text-xs text-signal hover:underline"
        >
          {new URL(item.url).hostname}
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
        {item.docs && (
          <a
            href={item.docs}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-xs text-info hover:underline"
          >
            {t.sources.docs}
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        )}
      </div>
    </div>
  );
}

function PlannedCard({ item, delay }: { item: SourceItem; delay: number }) {
  const { t } = useTranslation();
  return (
    <div
      className="animate-slide-in-right glass-card rounded-xl border border-border p-4 shadow-sm sm:p-5"
      style={{ animationDelay: `${300 + delay * 80}ms` }}
    >
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-bold text-text-primary">{item.name}</h3>
        <a
          href={item.url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1 text-xs text-signal hover:underline"
        >
          {new URL(item.url).hostname}
          <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
      <div className="space-y-2 text-sm">
        <p className="text-text-secondary">
          <span className="font-semibold text-warning">{t.sources.problem}</span> {item.problem}
        </p>
        <p className="text-text-muted">
          <span className="font-semibold text-signal">{t.sources.solution}</span> {item.possible_solution}
        </p>
      </div>
    </div>
  );
}
