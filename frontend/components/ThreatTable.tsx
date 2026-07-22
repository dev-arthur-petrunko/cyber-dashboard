"use client";

import { useState } from "react";
import Link from "next/link";
import { Threat, Explanation } from "@/lib/types";
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

async function fetchExplanation(threatId: number): Promise<Explanation | null> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const resp = await fetch(`${apiUrl}/threats/${threatId}/explain`);
    if (!resp.ok) return null;
    return await resp.json();
  } catch {
    return null;
  }
}

export function ThreatTable({ threats }: { threats: Threat[] }) {
  const { t } = useTranslation();
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [explanations, setExplanations] = useState<Record<number, Explanation>>({});
  const [loadingId, setLoadingId] = useState<number | null>(null);

  const toggleExpand = async (threatId: number) => {
    if (expandedId === threatId) {
      setExpandedId(null);
      return;
    }
    setExpandedId(threatId);
    
    // Fetch explanation if not already loaded
    if (!explanations[threatId]) {
      setLoadingId(threatId);
      const explanation = await fetchExplanation(threatId);
      if (explanation) {
        setExplanations(prev => ({ ...prev, [threatId]: explanation }));
      }
      setLoadingId(null);
    }
  };

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
              <ThreatRow
                key={threat.id}
                threat={threat}
                index={i}
                isExpanded={expandedId === threat.id}
                explanation={explanations[threat.id]}
                isLoading={loadingId === threat.id}
                onToggle={() => toggleExpand(threat.id)}
                t={t}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ThreatRow({
  threat,
  index,
  isExpanded,
  explanation,
  isLoading,
  onToggle,
  t,
}: {
  threat: Threat;
  index: number;
  isExpanded: boolean;
  explanation?: Explanation;
  isLoading: boolean;
  onToggle: () => void;
  t: any;
}) {
  return (
    <>
      <tr
        onClick={onToggle}
        className="animate-slide-in-right group relative cursor-pointer border-b border-border bg-panel last:border-0 transition-all duration-300 hover:bg-panel-raised/60 hover:shadow-md"
        style={{ animationDelay: `${Math.min(index * 40, 800)}ms` }}
      >
        <td className={`w-1 transition-all duration-300 group-hover:w-1.5 ${SEVERITY_BAR[threat.severity]}`} />
        <td className="whitespace-nowrap px-2 py-2.5 font-mono text-[10px] font-medium text-text-secondary sm:px-4 sm:py-3 sm:text-xs">{threat.source}</td>
        <td className="max-w-[180px] px-2 py-2.5 sm:max-w-md sm:px-4 sm:py-3">
          <div className="flex items-start gap-2">
            <svg
              className={`mt-0.5 h-4 w-4 flex-shrink-0 text-text-muted transition-transform duration-200 ${isExpanded ? "rotate-90" : ""}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
            <div className="min-w-0 flex-1">
              <span className="block truncate font-medium text-text-primary transition-colors group-hover:text-signal" title={threat.title}>
                {threat.title}
              </span>
              {threat.cve_id && (
                <Link
                  href={`/timeline/${threat.cve_id}`}
                  onClick={(e) => e.stopPropagation()}
                  className="mt-1 inline-flex items-center gap-1 rounded-md bg-signal/10 px-1.5 py-0.5 font-mono text-[10px] text-signal transition-colors hover:bg-signal/20 sm:text-xs"
                  title={t.table.showTimeline}
                >
                  {threat.cve_id}
                  <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </Link>
              )}
            </div>
          </div>
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
      
      {/* Expanded explanation row */}
      {isExpanded && (
        <tr className="border-b border-border bg-panel-raised/30">
          <td colSpan={8} className="px-4 py-4 sm:px-6">
            {isLoading ? (
              <div className="flex items-center gap-3 text-sm text-text-muted">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-signal border-t-transparent" />
                <span>{t.explain?.loading || "Завантаження..."}</span>
              </div>
            ) : explanation ? (
              <ExplanationContent explanation={explanation} threat={threat} t={t} />
            ) : (
              <p className="text-sm text-text-muted">{t.explain?.error || "Не вдалося завантажити пояснення"}</p>
            )}
          </td>
        </tr>
      )}
    </>
  );
}

function ExplanationContent({ explanation, threat, t }: { explanation: Explanation; threat: Threat; t: any }) {
  const explainLabels = t.explain || {};
  
  return (
    <div className="animate-fade-in space-y-4">
      {/* Explanation */}
      <div>
        <h4 className="mb-1.5 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted">
          <svg className="h-4 w-4 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {explainLabels.whatIs || "Що це?"}
        </h4>
        <p className="text-sm leading-relaxed text-text-secondary">{explanation.explanation}</p>
      </div>

      {/* Risk */}
      <div>
        <h4 className="mb-1.5 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted">
          <svg className="h-4 w-4 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {explainLabels.risk || "Ризик"}
        </h4>
        <p className="text-sm leading-relaxed text-text-secondary">{explanation.risk}</p>
      </div>

      {/* Recommendations */}
      <div>
        <h4 className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted">
          <svg className="h-4 w-4 text-signal" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {explainLabels.recommendations || "Рекомендації"}
        </h4>
        <ul className="space-y-1.5">
          {explanation.recommendations.map((rec, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
              <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-signal/60" />
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Link to original */}
      {threat.url && (
        <div className="pt-2">
          <a
            href={threat.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-panel px-3 py-1.5 text-xs font-medium text-text-secondary transition-all hover:border-signal/40 hover:text-signal"
            onClick={(e) => e.stopPropagation()}
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            {explainLabels.viewSource || "Переглянути джерело"}
          </a>
        </div>
      )}
    </div>
  );
}
