"""
Коллектор для CISA Known Exploited Vulnerabilities (KEV) Catalog.
Публичный JSON без ключа: https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
"""
import logging

import requests

from app.collectors.base import BaseCollector
from app.models.threat import ExploitMaturity, Severity, Threat, ThreatType

logger = logging.getLogger(__name__)

CISA_KEV_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)


class CISAKEVCollector(BaseCollector):
    source_name = "CISA KEV"

    def fetch(self) -> list[Threat]:
        try:
            resp = requests.get(CISA_KEV_URL, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error("CISA KEV fetch failed: %s", e)
            return []

        data = resp.json()
        threats = []
        for vuln in data.get("vulnerabilities", []):
            cve_id = vuln.get("cveID")
            if not cve_id:
                continue
            # Всё, что попало в KEV, по определению активно эксплуатируется —
            # это уже сигнал уровня Critical/High независимо от CVSS.
            severity = Severity.critical if vuln.get(
                "knownRansomwareCampaignUse"
            ) == "Known" else Severity.high

            threats.append(
                Threat(
                    external_id=cve_id,
                    cve_id=cve_id,
                    title=f"{cve_id}: {vuln.get('vulnerabilityName', '')}",
                    source=self.source_name,
                    type=ThreatType.cve,
                    severity=severity,
                    exploit_maturity=ExploitMaturity.in_the_wild,
                    vendor=vuln.get("vendorProject"),
                    products=[vuln.get("product")] if vuln.get("product") else [],
                    published=vuln.get("dateAdded"),
                    added_to_kev=vuln.get("dateAdded"),
                    summary=vuln.get("shortDescription", "")[:1000],
                    tags=["known-exploited", "ransomware"] if vuln.get(
                        "knownRansomwareCampaignUse"
                    ) == "Known" else ["known-exploited"],
                    url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                )
            )
        return threats
