"use client";

import Link from "next/link";
import { Threat } from "@/lib/types";
import { SeverityBadge, ExploitMaturityBadge } from "./SeverityBadge";
import { useTranslation } from "./LanguageContext";

const SEVERITY_BAR: Record<string, string> = {
  Critical: "bg-critical",
  High: "bg-warning",
  Medium: "bg-info",
  Low: "bg-border-strong",
  Unknown: "bg-border",
};

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const h = Math.floor(diffMs / 3600000);
  if (h < 1) return "<1г";
  if (h < 24) return `${h}г`;
  return `${Math.floor(h / 24)}д`;
}

export function ThreatTable({ threats }: { threats: Threat[] }) {
  const { t } = useTranslation();
  if (threats.length === 0) {
    return (
      <div className="glass-card rounded-xl border border-border p-8 text-center shadow-sm">
        <p className="text-sm text-text-secondary">{t.sections.noThreats}</p>
        <p className="mt-1 text-xs text-text-muted">{t.sections.tryFilter}</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-border shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[700px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border bg-gradient-to-r from-panel-raised via-panel-raised to-panel text-left text-[10px] uppercase tracking-wide text-text-secondary sm:text-xs">
              <th className="w-1" />
              <th className="px-2 py-2.5 font-semibold sm:px-4 sm:py-3">{t.table.source}</th>
              <th className="px-2 py-2.5 font-semibold sm:px-4 sm:py-3">{t.table.threat}</th>
              <th className="hidden px-4 py-3 font-semibold lg:table-cell">{t.table.vendor}</th>
              <th className="px-2 py-2.5 font-semibold sm:px-4 sm:py-3">{t.table.severity}</th>
              <th className="px-2 py-2.5 font-semibold sm:px-4 sm:py-3">{t.table.cvss}</th>
              <th className="px-2 py-2.5 font-semibold sm:px-4 sm:py-3">{t.table.status}</th>
              <th className="px-2 py-2.5 text-right font-semibold sm:px-4 sm:py-3">{t.table.when}</th>
            </tr>
          </thead>
          <tbody>
            {threats.map((threat, i) => (
              <tr
                key={threat.id}
                className="animate-slide-in-right group relative border-b border-border bg-panel last:border-0 transition-all duration-300 hover:bg-panel-raised/60 hover:shadow-md"
                style={{ animationDelay: `${Math.min(i * 40, 800)}ms` }}
              >
                <td className={`w-1 transition-all duration-300 group-hover:w-1.5 ${SEVERITY_BAR[threat.severity]}`} />
                <td className="whitespace-nowrap px-2 py-2.5 font-mono text-[10px] font-medium text-text-secondary sm:px-4 sm:py-3 sm:text-xs">{threat.source}</td>
                <td className="max-w-[180px] px-2 py-2.5 sm:max-w-md sm:px-4 sm:py-3">
                  <a
                    href={threat.url ?? undefined}
                    target="_blank"
                    rel="noreferrer"
                    className="block truncate font-medium text-text-primary transition-colors hover:text-signal hover:underline"
                    title={threat.title}
                  >
                    {threat.title}
                  </a>
                  {threat.cve_id && (
                    <Link
                      href={`/timeline/${threat.cve_id}`}
                      className="mt-1 inline-flex items-center gap-1 rounded-md bg-signal/10 px-1.5 py-0.5 font-mono text-[10px] text-signal transition-colors hover:bg-signal/20 sm:text-xs"
                      title={t.table.showTimeline}
                    >
                      {threat.cve_id}
                      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                    </Link>
                  )}
                </td>
                <td className="hidden whitespace-nowrap px-4 py-3 text-text-secondary lg:table-cell">{threat.vendor ?? "—"}</td>
                <td className="whitespace-nowrap px-2 py-2.5 sm:px-4 sm:py-3">
                  <SeverityBadge severity={threat.severity} />
                </td>
                <td className="whitespace-nowrap px-2 py-2.5 font-mono text-[10px] text-text-secondary sm:px-4 sm:py-3 sm:text-xs">
                  <span className={threat.cvss_score && threat.cvss_score >= 9 ? "font-bold text-critical" : ""}>
                    {threat.cvss_score?.toFixed(1) ?? "—"}
                  </span>
                </td>
                <td className="whitespace-nowrap px-2 py-2.5 sm:px-4 sm:py-3">
                  <ExploitMaturityBadge maturity={threat.exploit_maturity} />
                </td>
                <td className="whitespace-nowrap px-2 py-2.5 text-right text-[10px] text-text-muted sm:px-4 sm:py-3 sm:text-xs">
                  {timeAgo(threat.published)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
