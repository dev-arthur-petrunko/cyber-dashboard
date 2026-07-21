export type Region = "UA" | "World";
export type Severity = "Critical" | "High" | "Medium" | "Low" | "Unknown";
export type ExploitMaturity = "PoC" | "Weaponized" | "In the wild" | "Unknown";

export interface Threat {
  id: number;
  external_id: string;
  title: string;
  source: string;
  type: string;
  severity: Severity;
  country: string[];
  region: Region;
  vendor: string | null;
  products: string[];
  published: string;
  tags: string[];
  summary: string;
  url: string | null;
  cve_id: string | null;
  cvss_score: number | null;
  epss_score: number | null;
  exploit_maturity: ExploitMaturity;
}

export interface TimelineEvent {
  type: "published" | "poc" | "weaponized" | "kev" | "advisory" | "mention";
  label: string;
  date: string;
  source: string;
  title: string;
  url: string | null;
  severity: Severity;
}

export interface Timeline {
  cve_id: string;
  found: boolean;
  events: TimelineEvent[];
  days_to_poc: number | null;
  days_to_kev: number | null;
  cvss_score: number | null;
  epss_score: number | null;
  verdict: string;
}
export interface Stats {
  critical_threats: number;
  active_exploits: number;
  new_cve_24h: number;
  ua_alerts: number;
  high_epss_risk: number;
  risk_label?: string;
  top_vendors: { vendor: string; count: number }[];
  by_source: { source: string; count: number }[];
  total_threats: number;
  last_update: string | null;
}
