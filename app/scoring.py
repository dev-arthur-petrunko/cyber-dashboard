"""
Власна оцінка ризику (0–10) за методологією, наближеною до міжнародного CVSS.

Використовується як фолбек: коли джерело не надало офіційний CVSS,
ми рахуємо власну оцінку за тими ж принципами:
база за severity + бонуси за готовність експлойта, імовірність EPSS
та критичні ключові слова в заголовку/тегах. Діапазон 0–10.

Тут же живе витягування vendor з заголовка новинних записів,
коли джерело не вказало виробника (позначається * у таблиці).
"""
from __future__ import annotations

import re
from typing import Optional

# Базова оцінка за ярликом severity (0–10)
SEVERITY_BASE: dict[str, float] = {
    "Critical": 9.0,
    "High": 7.5,
    "Medium": 5.0,
    "Low": 2.0,
    "Unknown": 4.0,
}

# Бонус за рівень готовності експлойта
MATURITY_BUMP: dict[str, float] = {
    "In the wild": 1.2,
    "Weaponized": 0.8,
    "PoC": 0.5,
    "Unknown": 0.0,
}

# Ключові слова, що підвищують ризик (заголовок / теги)
HIGH_RISK_KEYWORDS: tuple[str, ...] = (
    "ransomware", "exploit", "zero-day", "zeroday", "critical",
    "apt", "spyware", "malware", "botnet", "backdoor", "remote code",
    "критичн", "вимагач", "експлойт", "шкідлив",
)


def compute_local_score(
    severity: Optional[str] = None,
    exploit_maturity: Optional[str] = None,
    epss_score: Optional[float] = None,
    title: Optional[str] = None,
    tags: Optional[list] = None,
) -> Optional[float]:
    """Власна оцінка ризику (0–10) або None, якщо даних замало."""
    if not severity and epss_score is None:
        return None

    score = SEVERITY_BASE.get(severity or "Unknown", 4.0)

    score += MATURITY_BUMP.get(exploit_maturity or "Unknown", 0.0)

    # EPSS: імовірність експлуатації протягом 30 днів (0–1) → максимум +2.0
    if epss_score is not None:
        score += max(0.0, min(float(epss_score), 1.0)) * 2.0

    # Критичні ключові слова в заголовку/тегах → до +0.6
    haystack = " ".join([
        (title or "").lower(),
        *(str(t).lower() for t in (tags or [])),
    ])
    if any(kw in haystack for kw in HIGH_RISK_KEYWORDS):
        score += 0.6

    return round(max(0.0, min(score, 10.0)), 1)


# Відомі вендори та їх ключові слова для витягування з заголовка/тегів.
# Ключі вже в нижньому регістрі; пошук йде найдовшим збігом першим.
VENDOR_KEYWORDS: dict[str, str] = {
    "palo alto networks": "Palo Alto Networks",
    "palo alto": "Palo Alto Networks",
    "pan-os": "Palo Alto Networks",
    "microsoft": "Microsoft",
    "sharepoint": "Microsoft",
    "windows": "Microsoft",
    "azure": "Microsoft",
    "exchange server": "Microsoft",
    "outlook": "Microsoft",
    "office": "Microsoft",
    "active directory": "Microsoft",
    "m365": "Microsoft",
    "cisco": "Cisco",
    "webex": "Cisco",
    "fortinet": "Fortinet",
    "fortios": "Fortinet",
    "adobe": "Adobe",
    "acrobat": "Adobe",
    "oracle": "Oracle",
    "weblogic": "Oracle",
    "vmware": "VMware",
    "vsphere": "VMware",
    "citrix": "Citrix",
    "google": "Google",
    "chrome": "Google",
    "android": "Google",
    "apple": "Apple",
    "macos": "Apple",
    "ios": "Apple",
    "iphone": "Apple",
    "linux": "Linux",
    "kernel": "Linux",
    "apache": "Apache",
    "nginx": "Nginx",
    "wordpress": "WordPress",
    "php": "PHP",
    "jenkins": "Jenkins",
    "grafana": "Grafana",
    "atlassian": "Atlassian",
    "jira": "Atlassian",
    "confluence": "Atlassian",
    "bitbucket": "Atlassian",
    "sonicwall": "SonicWall",
    "sophos": "Sophos",
    "netgear": "Netgear",
    "tp-link": "TP-Link",
    "d-link": "D-Link",
    "drupal": "Drupal",
    "exim": "Exim",
    "openssl": "OpenSSL",
    "openvpn": "OpenVPN",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sap": "SAP",
    "samsung": "Samsung",
    "hpe": "HPE",
    "aruba": "HPE",
    "ibm": "IBM",
    "dell": "Dell",
    "lenovo": "Lenovo",
    "intel": "Intel",
    "nvidia": "NVIDIA",
    "qualcomm": "Qualcomm",
    "qnap": "QNAP",
    "synology": "Synology",
    "zimbra": "Zimbra",
    "solarwinds": "SolarWinds",
    "kaspersky": "Kaspersky",
    "eset": "ESET",
    "mikrotik": "MikroTik",
    "siemens": "Siemens",
    "zoom": "Zoom",
    "slack": "Slack",
    "mozilla": "Mozilla",
    "firefox": "Mozilla",
    "ubuntu": "Ubuntu",
    "debian": "Debian",
    "red hat": "Red Hat",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "gitlab": "GitLab",
    "teamviewer": "TeamViewer",
    "anydesk": "AnyDesk",
    "aws": "Amazon Web Services",
    "amazon": "Amazon",
    "wifi": "Wi-Fi",
}


def extract_vendor(
    title: Optional[str] = None,
    summary: Optional[str] = None,
    tags: Optional[list] = None,
) -> Optional[str]:
    """Витягує назву виробника з заголовка/тегів або None, якщо не знайдено."""
    parts = [title or "", summary or ""]
    parts.extend(str(t) for t in (tags or []))
    text = " ".join(parts).lower()

    for keyword in sorted(VENDOR_KEYWORDS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(keyword) + r"\b", text):
            return VENDOR_KEYWORDS[keyword]
    return None
