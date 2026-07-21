"use client";

import { Severity, ExploitMaturity } from "@/lib/types";
import { useTranslation } from "./LanguageContext";

const SEVERITY_COLOR: Record<Severity, string> = {
  Critical: "text-critical border-critical/40 bg-critical/10",
  High: "text-warning border-warning/40 bg-warning/10",
  Medium: "text-info border-info/40 bg-info/10",
  Low: "text-text-secondary border-border-strong bg-panel-raised",
  Unknown: "text-text-muted border-border bg-panel",
};

export function SeverityBadge({ severity }: { severity: Severity }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 font-mono text-[11px] font-semibold uppercase tracking-wide transition-all duration-300 hover:scale-105 ${SEVERITY_COLOR[severity]}`}
    >
      {(severity === "Critical" || severity === "High") && (
        <span className={`h-1.5 w-1.5 rounded-full ${severity === "Critical" ? "bg-critical animate-pulse" : "bg-warning"}`} />
      )}
      {severity}
    </span>
  );
}

export function ExploitMaturityBadge({ maturity }: { maturity: ExploitMaturity }) {
  const { t } = useTranslation();

  const MATURITY_LABEL: Record<ExploitMaturity, string> = {
    PoC: t.exploitStatus.poc,
    Weaponized: t.exploitStatus.weaponized,
    "In the wild": t.exploitStatus.inTheWild,
    Unknown: "—",
  };

  if (maturity === "Unknown") {
    return <span className="text-text-muted text-xs">—</span>;
  }
  const dotColor =
    maturity === "In the wild" ? "bg-critical" : maturity === "Weaponized" ? "bg-warning" : "bg-signal";
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-text-secondary">
      <span className={`h-2 w-2 rounded-full ${dotColor} animate-pulse`} />
      {MATURITY_LABEL[maturity]}
    </span>
  );
}
