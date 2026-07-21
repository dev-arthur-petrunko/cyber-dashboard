import { Timeline, TimelineEvent } from "@/lib/types";
import { SeverityBadge } from "./SeverityBadge";

const DOT_COLOR: Record<TimelineEvent["type"], string> = {
  published: "bg-info",
  poc: "bg-signal",
  weaponized: "bg-warning",
  kev: "bg-critical",
  advisory: "bg-ua-gold",
  mention: "bg-border-strong",
};

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("uk-UA", { day: "2-digit", month: "short", year: "numeric" });
}

export function CyberTimeline({ timeline }: { timeline: Timeline }) {
  if (!timeline.found) {
    return (
      <div className="rounded-xl border border-border bg-panel p-8 text-center shadow-sm">
        <p className="text-sm text-text-secondary">
          По <span className="font-mono font-bold text-text-primary">{timeline.cve_id}</span> поки немає даних у базі.
        </p>
        <p className="mt-1 text-xs text-text-muted">
          Можливо, колектори ще не збирали цей CVE — запусти <code className="rounded bg-panel-raised px-1.5 py-0.5 font-mono text-xs">python -m app.pipeline</code>.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Metric label="CVSS" value={timeline.cvss_score?.toFixed(1) ?? "—"} />
        <Metric label="EPSS" value={timeline.epss_score != null ? `${Math.round(timeline.epss_score * 100)}%` : "—"} />
        <Metric label="До PoC" value={timeline.days_to_poc != null ? `${timeline.days_to_poc} дн.` : "—"} />
        <Metric label="До KEV" value={timeline.days_to_kev != null ? `${timeline.days_to_kev} дн.` : "—"} accent="critical" />
      </div>

      <div className="mb-6 rounded-xl border border-signal/30 bg-gradient-to-r from-signal/5 to-info/5 p-5 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-wide text-signal">Висновок</p>
        <p className="mt-2 text-sm font-medium text-text-primary">{timeline.verdict}</p>
      </div>

      <ol className="relative border-l-2 border-border pl-6">
        {timeline.events.map((e, i) => (
          <li key={i} className="mb-6 last:mb-0">
            <span
              className={`absolute -left-[6px] mt-1.5 h-3 w-3 rounded-full ring-4 ring-bg ${DOT_COLOR[e.type]} shadow-sm`}
            />
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-md bg-panel-raised px-2 py-1 font-mono text-xs text-text-muted">{formatDate(e.date)}</span>
              <span className="text-xs text-text-secondary">·</span>
              <span className="text-xs font-medium text-text-secondary">{e.source}</span>
              {e.severity !== "Unknown" && <SeverityBadge severity={e.severity} />}
            </div>
            <p className="mt-2 text-sm font-semibold text-text-primary">{e.label}</p>
            {e.url ? (
              <a href={e.url} target="_blank" rel="noreferrer" className="mt-1 inline-flex items-center gap-1 text-xs text-text-secondary hover:text-signal hover:underline transition-colors">
                {e.title}
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            ) : (
              <p className="mt-1 text-xs text-text-secondary">{e.title}</p>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: "critical" }) {
  return (
    <div className="rounded-xl border border-border bg-panel p-4 shadow-sm">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-text-secondary">{label}</p>
      <p className={`mt-1.5 font-mono text-xl font-bold ${accent === "critical" ? "text-critical" : "text-text-primary"}`}>
        {value}
      </p>
    </div>
  );
}
