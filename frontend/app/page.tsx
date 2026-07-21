"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchStats, fetchThreats } from "@/lib/api";
import { Region, Stats, Threat } from "@/lib/types";
import { PulseStrip } from "@/components/PulseStrip";
import { RegionToggle } from "@/components/RegionToggle";
import { StatCard } from "@/components/StatCard";
import { VendorChart } from "@/components/VendorChart";
import { ThreatTable } from "@/components/ThreatTable";
import { ThemeToggle } from "@/components/ThemeToggle";
import { LanguageToggle } from "@/components/LanguageToggle";
import { UaFlag } from "@/components/UaFlag";
import { useTranslation } from "@/components/LanguageContext";

const DEMO_PULSE = [2, 3, 2, 4, 3, 5, 4, 6, 5, 7, 6, 8, 9, 7, 8, 10, 9, 11, 8, 7, 9, 10, 8, 6];

export default function DashboardPage() {
  const { t } = useTranslation();
  const [region, setRegion] = useState<Region | undefined>(undefined);
  const [stats, setStats] = useState<Stats | null>(null);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [isDemo, setIsDemo] = useState(false);
  const [loading, setLoading] = useState(true);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([fetchStats(region), fetchThreats(region, 50)]).then(([s, t]) => {
      if (cancelled) return;
      setStats(s.data);
      setThreats(t.data.items);
      setIsDemo(s.isDemo || t.isDemo);
      setLoading(false);
    });
    return () => { cancelled = true; };
  }, [region]);

  const severityBreakdown = threats.reduce<Record<string, number>>((acc, t) => {
    acc[t.severity] = (acc[t.severity] ?? 0) + 1;
    return acc;
  }, {});

  const exploitBreakdown = threats.reduce<Record<string, number>>((acc, t) => {
    const key = t.exploit_maturity || "Unknown";
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});

  const recentThreats = threats.slice(0, 5);

  return (
    <main className="mesh-gradient-bg min-h-screen bg-bg">
      {/* Animated background orbs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="animate-glow-pulse absolute -top-40 -left-40 h-80 w-80 rounded-full bg-signal/5 blur-3xl" />
        <div className="animate-glow-pulse absolute top-1/3 -right-20 h-60 w-60 rounded-full bg-info/5 blur-3xl" style={{ animationDelay: '1s' }} />
        <div className="animate-glow-pulse absolute -bottom-20 left-1/3 h-72 w-72 rounded-full bg-critical/3 blur-3xl" style={{ animationDelay: '2s' }} />
      </div>

      <PulseStrip hourlyVolume={DEMO_PULSE} />

      <div className="relative z-10 mx-auto max-w-7xl px-3 py-3 sm:px-4 sm:py-4 lg:px-8 lg:py-8">
        {/* Header — mobile: stacked, desktop: row */}
        <header className="animate-fade-in-up mb-4 flex flex-col gap-3 sm:mb-6 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="gradient-border flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-ua-blue to-signal shadow-lg sm:h-11 sm:w-11">
              <svg className="h-4 w-4 text-white sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="font-mono text-sm font-black tracking-tight text-text-primary sm:text-lg lg:text-xl">
                UA CYBER THREAT
              </h1>
              <p className="truncate text-[11px] text-text-secondary sm:text-sm">
                {stats?.total_threats ?? "—"} {t.header.records}
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-3">
            <RegionToggle value={region} onChange={setRegion} />
            <Link
              href="/sources"
              className="inline-flex items-center gap-1 rounded-lg border border-border bg-panel px-2 py-1.5 text-[11px] font-medium text-text-secondary shadow-sm transition-all hover:border-signal/40 hover:text-signal sm:px-3 sm:py-2 sm:text-sm"
            >
              <svg className="h-3.5 w-3.5 sm:h-4 sm:w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span className="hidden sm:inline">{t.header.sources}</span>
            </Link>
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </header>

        {isDemo && (
          <div className="animate-fade-in mb-4 rounded-xl border border-warning/30 bg-warning/10 px-3 py-2.5 text-xs text-warning shadow-sm sm:mb-6 sm:px-4 sm:py-3 sm:text-sm">
            ⚠️ {t.header.demoWarning}
          </div>
        )}

        {/* Stat Cards — responsive grid */}
        <section className="mb-4 grid grid-cols-2 gap-2 sm:mb-8 sm:gap-4 lg:grid-cols-5">
          <div className="premium-glow">
            <StatCard label={t.stats.critical} value={stats?.critical_threats ?? "—"} accent="critical" icon={<BoltIcon />} delay={0} />
          </div>
          <div className="premium-glow">
            <StatCard label={t.stats.active} value={stats?.active_exploits ?? "—"} accent="warning" icon={<TargetIcon />} delay={80} />
          </div>
          <div className="premium-glow">
            <StatCard label={t.stats.new24h} value={stats?.new_cve_24h ?? "—"} accent="signal" icon={<SparklesIcon />} delay={160} />
          </div>
          {region !== "World" && (
            <div className="premium-glow col-span-2 sm:col-span-1">
              <StatCard label={t.stats.uaAlerts} value={stats?.ua_alerts ?? "—"} icon={<UaFlag className="h-5 w-8 rounded shadow-sm sm:h-6 sm:w-9" />} delay={240} />
            </div>
          )}
          <div className={`premium-glow ${region !== "World" ? "col-span-2 sm:col-span-1" : ""}`}>
            <StatCard label={stats?.risk_label === "High/Critical" ? t.stats.highSeverity : t.stats.epssRisk} value={stats?.high_epss_risk ?? "—"} accent="warning" icon={<ChartIcon />} delay={region === "World" ? 240 : 320} />
          </div>
        </section>

        {/* Sources + Vendor Chart */}
        <section className="mb-6 grid grid-cols-1 gap-4 sm:mb-8 lg:grid-cols-3">
          <div className="animate-fade-in-up glass-card rounded-xl border border-border p-4 shadow-sm sm:p-5 lg:col-span-2" style={{ animationDelay: "200ms" }}>
            <h2 className="mb-3 flex items-center gap-2 text-xs font-bold text-text-secondary sm:mb-4 sm:text-sm">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-signal" />
              {t.sections.bySource}
            </h2>
            <div className="flex flex-wrap gap-2">
              {stats?.by_source.map((s, i) => (
                <span
                  key={s.source}
                  className="animate-fade-in inline-flex items-center gap-1.5 rounded-full border border-border bg-panel-raised/80 px-2.5 py-1 text-[11px] font-medium text-text-secondary shadow-sm transition-all hover:scale-105 hover:shadow-md sm:px-3 sm:py-1.5 sm:text-xs"
                  style={{ animationDelay: `${300 + i * 50}ms` }}
                >
                  {s.source}
                  <span className="font-mono font-bold text-text-primary">{s.count}</span>
                </span>
              ))}
            </div>
          </div>
          <div className="animate-fade-in-up glass-card rounded-xl border border-border p-4 shadow-sm sm:p-5" style={{ animationDelay: "300ms" }}>
            <h2 className="mb-2 flex items-center gap-2 text-xs font-bold text-text-secondary sm:text-sm">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-critical" />
              {t.sections.topVendors}
            </h2>
            <VendorChart data={stats?.top_vendors ?? []} />
          </div>
        </section>

        {/* Details */}
        <section className="animate-fade-in-up mb-6 sm:mb-8" style={{ animationDelay: "400ms" }}>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="group mb-3 flex items-center gap-2 text-sm font-bold text-text-secondary transition-all hover:text-signal sm:mb-4"
          >
            <svg className={`h-5 w-5 transition-transform duration-300 ${showDetails ? "rotate-90" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            {t.sections.details}
          </button>

          {showDetails && (
            <div className="animate-fade-in-up grid grid-cols-1 gap-3 sm:gap-4 lg:grid-cols-3">
              <DetailCard title={t.sections.severity} icon={<WarningIcon />}>
                <div className="space-y-2">
                  {["Critical", "High", "Medium", "Low"].map((sev) => {
                    const count = severityBreakdown[sev] ?? 0;
                    const total = threats.length || 1;
                    const pct = Math.round((count / total) * 100);
                    const colors: Record<string, string> = {
                      Critical: "bg-critical", High: "bg-warning", Medium: "bg-info", Low: "bg-border-strong"
                    };
                    return (
                      <div key={sev}>
                        <div className="mb-1 flex justify-between text-xs text-text-secondary">
                          <span className="font-medium">{sev}</span>
                          <span className="font-mono">{count} ({pct}%)</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-panel-raised">
                          <div className={`h-full rounded-full ${colors[sev]} transition-all duration-1000 ease-out`} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </DetailCard>

              <DetailCard title={t.sections.exploitStatus} icon={<TargetIconSmall />}>
                <div className="space-y-3">
                  {(["In the wild", "Weaponized", "PoC", "Unknown"] as const).map((status) => {
                    const count = exploitBreakdown[status] ?? 0;
                    if (count === 0) return null;
                    const dotColor = status === "In the wild" ? "bg-critical animate-pulse" : status === "Weaponized" ? "bg-warning" : status === "PoC" ? "bg-signal" : "bg-border-strong";
                    const label = status === "In the wild" ? t.exploitStatus.inTheWild : status === "Weaponized" ? t.exploitStatus.weaponized : status === "PoC" ? t.exploitStatus.poc : t.exploitStatus.unknown;
                    return (
                      <div key={status} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className={`h-2.5 w-2.5 rounded-full ${dotColor}`} />
                          <span className="text-sm text-text-secondary">{label}</span>
                        </div>
                        <span className="font-mono text-sm font-bold text-text-primary">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </DetailCard>

              <DetailCard title={t.sections.recentThreats} icon={<ClockIcon />}>
                <div className="space-y-2.5">
                  {recentThreats.map((threat) => (
                    <div key={threat.id} className="group flex items-start gap-2">
                      <span className={`mt-1.5 h-2 w-2 flex-shrink-0 rounded-full ${threat.severity === "Critical" ? "bg-critical" : threat.severity === "High" ? "bg-warning" : "bg-info"}`} />
                      <div className="min-w-0 flex-1">
                        <a href={threat.url ?? "#"} target="_blank" rel="noreferrer" className="block truncate text-xs font-medium text-text-primary transition-colors hover:text-signal">
                          {threat.title}
                        </a>
                        <p className="mt-0.5 truncate text-[10px] text-text-muted">{threat.source} · {threat.severity}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </DetailCard>
            </div>
          )}
        </section>

        {/* Threats Table */}
        <section className="animate-fade-in-up" style={{ animationDelay: "500ms" }}>
          <h2 className="mb-3 flex items-center gap-2 text-xs font-bold text-text-secondary sm:mb-4 sm:text-sm">
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-warning" />
            {t.sections.latestThreats}
          </h2>
          {loading ? (
            <div className="glass-card rounded-xl border border-border p-8 text-center shadow-sm">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-signal border-t-transparent" />
              <p className="mt-3 text-sm text-text-muted">{t.sections.loading}</p>
            </div>
          ) : (
            <ThreatTable threats={threats.slice(0, 25)} />
          )}
        </section>
      </div>
    </main>
  );
}

function DetailCard({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="glass-card rounded-xl border border-border p-4 shadow-sm sm:p-5">
      <h3 className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted">
        {icon}
        {title}
      </h3>
      {children}
    </div>
  );
}

function BoltIcon() {
  return (
    <svg className="h-5 w-5 text-critical sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  );
}

function TargetIcon() {
  return (
    <svg className="h-5 w-5 text-warning sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
    </svg>
  );
}

function SparklesIcon() {
  return (
    <svg className="h-5 w-5 text-signal sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg className="h-5 w-5 text-warning sm:h-6 sm:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg className="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  );
}

function TargetIconSmall() {
  return (
    <svg className="h-4 w-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg className="h-4 w-4 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}
