"""Робота з відкритими STIX-даними MITRE ATT&CK."""
from functools import lru_cache

import requests

ATTACK_STIX_URL = (
    "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/"
    "enterprise-attack/enterprise-attack.json"
)


@lru_cache(maxsize=1)
def load_groups() -> list[dict]:
    """Повертає активні групи ATT&CK та їхні техніки з кешем процесу."""
    response = requests.get(ATTACK_STIX_URL, timeout=45)
    response.raise_for_status()
    objects = response.json().get("objects", [])

    techniques = {
        item["id"]: next(
            (
                ref.get("external_id")
                for ref in item.get("external_references", [])
                if ref.get("source_name") == "mitre-attack"
            ),
            None,
        )
        for item in objects
        if item.get("type") == "attack-pattern"
    }
    relationships: dict[str, list[str]] = {}
    for item in objects:
        if item.get("type") != "relationship" or item.get("relationship_type") != "uses":
            continue
        technique_id = techniques.get(item.get("target_ref"))
        if technique_id:
            relationships.setdefault(item.get("source_ref"), []).append(technique_id)

    groups = []
    for item in objects:
        if item.get("type") != "intrusion-set" or item.get("revoked") or item.get("x_mitre_deprecated"):
            continue
        attack_id = next(
            (
                ref.get("external_id")
                for ref in item.get("external_references", [])
                if ref.get("source_name") == "mitre-attack"
            ),
            None,
        )
        if not attack_id:
            continue
        groups.append(
            {
                "id": attack_id,
                "name": item.get("name"),
                "aliases": item.get("aliases") or [],
                "description": item.get("description", ""),
                "techniques": sorted(set(relationships.get(item["id"], []))),
                "url": f"https://attack.mitre.org/groups/{attack_id}/",
            }
        )
    return sorted(groups, key=lambda group: group["name"].lower())


def search_groups(query: str | None = None, limit: int = 50) -> list[dict]:
    groups = load_groups()
    if query:
        needle = query.lower().strip()
        groups = [
            group for group in groups
            if needle in group["name"].lower()
            or any(needle in alias.lower() for alias in group["aliases"])
        ]
    return groups[:limit]
