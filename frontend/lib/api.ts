import { Stats, Threat, Region, Timeline, Severity, ExploitMaturity } from "./types";
import curatedRaw from "../../data/curated_threats.json";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type CuratedItem = {
  title: string;
  url: string;
  source: string;
  region: Region;
  type: string;
  severity: Severity;
  country: string[];
  tags: string[];
  summary: string;
  published: string;
  exploit_maturity: ExploitMaturity;
  vendor?: string | null;
};

const CURATED_THREATS: Threat[] = (curatedRaw as CuratedItem[]).map((item, i) => ({
  id: i + 1,
  external_id: item.url,
  title: item.title,
  source: item.source,
  type: item.type,
  severity: item.severity,
  country: item.country,
  region: item.region,
  vendor: item.vendor ?? null,
  products: [],
  published: item.published,
  tags: item.tags,
  summary: item.summary,
  url: item.url,
  cve_id: null,
  cvss_score: null,
  epss_score: null,
  exploit_maturity: item.exploit_maturity,
}));

const uaCount = CURATED_THREATS.filter((t) => t.region === "UA").length;
const criticalCount = CURATED_THREATS.filter((t) => t.severity === "Critical").length;
const activeExploits = CURATED_THREATS.filter(
  (t) => t.exploit_maturity === "In the wild" || t.exploit_maturity === "Weaponized"
).length;

const sourceCounts = CURATED_THREATS.reduce<Record<string, number>>((acc, t) => {
  acc[t.source] = (acc[t.source] ?? 0) + 1;
  return acc;
}, {});

const DEMO_STATS: Stats = {
  critical_threats: criticalCount,
  active_exploits: activeExploits,
  new_cve_24h: 0,
  ua_alerts: uaCount,
  high_epss_risk: 0,
  top_vendors: [],
  by_source: Object.entries(sourceCounts)
    .map(([source, count]) => ({ source, count }))
    .sort((a, b) => b.count - a.count),
  total_threats: CURATED_THREATS.length,
  last_update: new Date().toISOString(),
};

const DEMO_THREATS: Threat[] = [...CURATED_THREATS].sort(
  (a, b) => new Date(b.published).getTime() - new Date(a.published).getTime()
);

async function safeFetch<T>(path: string, fallback: T): Promise<{ data: T; isDemo: boolean }> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${API_URL}${path}`, { cache: "no-store", signal: controller.signal });
    clearTimeout(timeoutId);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return { data: await res.json(), isDemo: false };
  } catch {
    return { data: fallback, isDemo: true };
  }
}

export async function fetchStats(region?: Region) {
  const qs = region ? `?region=${region}` : "";
  const stats = { ...DEMO_STATS };
  if (region) {
    const filtered = CURATED_THREATS.filter((t) => t.region === region);
    stats.total_threats = filtered.length;
    stats.critical_threats = filtered.filter((t) => t.severity === "Critical").length;
    stats.ua_alerts = region === "UA" ? filtered.length : 0;
    stats.active_exploits = filtered.filter(
      (t) => t.exploit_maturity === "In the wild" || t.exploit_maturity === "Weaponized"
    ).length;
    const bySource = filtered.reduce<Record<string, number>>((acc, t) => {
      acc[t.source] = (acc[t.source] ?? 0) + 1;
      return acc;
    }, {});
    stats.by_source = Object.entries(bySource).map(([source, count]) => ({ source, count }));
  }
  return safeFetch<Stats>(`/stats${qs}`, stats);
}

const DEMO_TIMELINE: Timeline = {
  cve_id: "CVE-2026-1287",
  found: true,
  verdict: "Критична швидкість: почали атакувати практично одразу після публікації — патчити невідкладно.",
  days_to_poc: 1,
  days_to_kev: 3,
  cvss_score: 9.8,
  epss_score: 0.94,
  events: [
    {
      type: "published", label: "Уязвимість опублікована", date: new Date(Date.now() - 4 * 86400e3).toISOString(),
      source: "NVD", title: "CVE-2026-1287", url: null, severity: "Critical",
    },
    {
      type: "poc", label: "З'явився публічний PoC", date: new Date(Date.now() - 3 * 86400e3).toISOString(),
      source: "GitHub", title: "PoC: CVE-2026-1287-exploit", url: "https://github.com", severity: "Unknown",
    },
    {
      type: "kev", label: "Додано в CISA KEV (активна експлуатація)", date: new Date(Date.now() - 1 * 86400e3).toISOString(),
      source: "CISA KEV", title: "CVE-2026-1287 KEV", url: null, severity: "Critical",
    },
  ],
};

export async function fetchTimeline(cveId: string) {
  return safeFetch<Timeline>(`/timeline/${cveId}`, { ...DEMO_TIMELINE, cve_id: cveId });
}

export async function fetchThreats(region?: Region, limit = 25) {
  const qs = new URLSearchParams({
    limit: String(limit),
    days: "365",
    ...(region ? { region } : {}),
  });
  const filtered = region ? DEMO_THREATS.filter((t) => t.region === region) : DEMO_THREATS;
  return safeFetch<{ total: number; items: Threat[] }>(`/threats?${qs}`, {
    total: filtered.length,
    items: filtered.slice(0, limit),
  });
}
