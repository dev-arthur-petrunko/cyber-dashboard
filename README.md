# UA Cyber Threat Dashboard

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)

A cybersecurity threat aggregator for Ukraine: it collects data from 10 sources
(NVD, CISA KEV, CERT-UA, ThreatFox, and others), normalizes them into a single
data model, and exposes it through a REST API. It ships with its own Next.js
dashboard and automatically publishes summaries to Telegram via n8n.

🔗 **Demo:** [cyber-dashboard-gamma.vercel.app](https://cyber-dashboard-gamma.vercel.app)
🔗 **Repository:** [github.com/dev-arthur-petrunko/cyber-dashboard](https://github.com/dev-arthur-petrunko/cyber-dashboard)

<h3 align="center">
This is what the project is becoming — it's getting closer to this vision step by step,<br>
and it moves forward only with your support 🚀 Soon I will post a link to the site here and you can use it and help with the development of this project.
</h3>

```bash
The link will be here ---> (Not yet)
```

<p align="center">
  <img src="https://raw.githubusercontent.com/dev-arthur-petrunko/cyber-dashboard/main/images/Main.png" alt="Main" width="100%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/dev-arthur-petrunko/cyber-dashboard/main/images/Main_below.png" alt="Main below" width="100%">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/dev-arthur-petrunko/cyber-dashboard/main/images/Base.png" alt="Base" width="100%">
</p>

---

## Architecture

```
Collectors (10 sources, see table below)
↓
Normalizer (inside each collector → Threat)
↓
Storage (upsert with deduplication) → EPSS enrichment
↓
PostgreSQL (Neon)
↓
FastAPI (Render) → /threats?region=UA|World /stats /health
↓
┌─────────────────────┬──────────────────────────┐
↓ ↓
Dashboard (Next.js, Vercel) n8n Webhook → AI Agent → Telegram
```

## Data Sources

| Source | Region | Type | Status |
|---|---|---|---|
| NVD | World | CVE + CVSS score | ✅ real API |
| CISA KEV | World | actively exploited CVEs | ✅ real API |
| GitHub | World | PoC exploits | ✅ |
| Exploit-DB | World | ready-made exploits | ✅ |
| The Hacker News / BleepingComputer | World | news | ✅ RSS |
| NCSC UK | World | official threat reports | ✅ RSS |
| ThreatFox (abuse.ch) | World | IOCs (malicious IPs/domains/hashes) | ✅ real API |
| MalwareBazaar | World | malware samples | ✅ real API |
| AlienVault OTX | World | pulse reports | ✅ |
| CERT-UA | UA | advisories | ✅ RSS |
| Cyber Police of Ukraine | UA | news | ✅ |
| SSSCIP (State Service of Special Communication) | UA | news | ✅ |
| NCCC under the NSDC | UA | news | ✅ |
| SSU / Cybersecurity Department | UA | news | ⚠️ scraper, depends on site layout |
| Vendor RSS | UA | vendor publications about Ukraine | ✅ |

## Risk Metrics (not just a Severity label)

- **CVSS score** — how technically dangerous the vulnerability is (0–10)
- **EPSS score** — probability of real-world exploitation within the next 30 days (0–1), updated in a separate step at the end of the pipeline
- **Exploit maturity** — `PoC` (code available on GitHub) → `Weaponized` (ready-made exploit on Exploit-DB) → `In the wild` (in CISA KEV, meaning it's actively being exploited)

## Values marked with `*` — internal estimate (no official data)

If a value in the table has an asterisk `*` (e.g. `7.3*` or `Microsoft*`), it
means the source **did not provide official data**, and the value was
calculated by us using the same principles (`app/scoring.py`):

- **CVSS `*`** (`compute_local_score`) — our own **0–10** risk estimate using
  a methodology close to the international CVSS standard, used when an
  official score is unavailable (for example, NVD no longer returns
  CVSS/CPE data for some new 2026 CVEs).
  Formula:
  - base by `severity`: Critical = 9.0, High = 7.5, Medium = 5.0, Low = 2.0, Unknown = 4.0
  - `+` exploit maturity: In the wild = 1.2, Weaponized = 0.8, PoC = 0.5
  - `+` EPSS (probability of exploitation within 30 days, 0–1): up to +2.0
  - `+` critical keywords in the title/tags (ransomware, zero-day, APT...): +0.6
  - result is capped to the **0–10** range
- **Vendor `*`** (`extract_vendor`) — the vendor is inferred from the news
  item's title (e.g. "Critical SharePoint RCE…" → `Microsoft*`) when the
  source didn't specify one. A dictionary of known vendors is used
  (Microsoft, Cisco, Fortinet, Palo Alto Networks, Adobe, …).

There is **no asterisk** if the value is official and came directly from the source.

## IOC Feed

The "Latest Threats" table shows only news, CVEs, and advisories.
IOC indicators (malicious IPs/domains/hashes) from ThreatFox, MalwareBazaar,
and AlienVault OTX are moved into a separate, collapsible **"IOC Feed
(Indicators)"** section — a horizontal strip of cards showing the indicator
value, source, and a link to the original. API filter: `GET /threats?category=feed`
(excludes IOCs) or `?category=ioc` (IOCs only).

## What's Done

- [x] 10 collectors (UA + World), a unified `Threat` model, deduplication, EPSS enrichment
- [x] REST API on FastAPI: `/threats`, `/stats`, `/timeline/{cve}`, `/health`
- [x] Next.js dashboard: KPI tiles, top vendors, threats table, Ukraine/World toggle
- [x] Cyber Timeline — CVE history (publication → PoC → CISA KEV) with an exploitation-speed verdict
- [x] Automated collection via GitHub Actions cron — no dedicated server needed for the pipeline
- [x] Backend deployed on **Render** (Python/FastAPI, free tier)
- [x] Database — **PostgreSQL on Neon** (free tier)
- [x] Frontend deployed on **Vercel**
- [x] **AI Automation via n8n**: after every pipeline run, data is sent to an n8n webhook → AI Agent (Groq + SerpAPI to look up context for unfamiliar threats) analyzes the summary → a formatted post is automatically published to a Telegram channel

## Automation: pipeline → n8n → Telegram

After each run of `app/pipeline.py` completes (including collection from all
sources and EPSS enrichment), the data is **automatically sent via a POST
request** to an n8n webhook:

What happens on the n8n side:
1. **Webhook** receives a JSON payload with statistics (`stats`) and the list of new threats (`new_threats`)
2. **AI Agent** analyzes the data, picks the 3–5 most important threats (priority: Critical + active exploitation, then UA region), and for unclear campaigns/malware performs **one** search query via SerpAPI to explain what it is and provide a practical recommendation
3. **Code node** formats the response for Telegram: emoji, structure, 900-character limit
4. **Telegram node** publishes the final post to the channel

Configured via `N8N_WEBHOOK_URL` (see below).

## Quick Start (Backend)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Collect data
python -m app.pipeline

# Start the API
uvicorn app.main:app --reload
# → http://localhost:8000/docs — Swagger UI with all endpoints
```

## Quick Start (Frontend)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=<backend address>
npm run dev
# → http://localhost:3000
```

If the backend is unavailable, the frontend honestly shows a banner and
demo data instead of failing with a blank screen.

⚠️ **About cold starts:** the backend on Render (free tier) goes to sleep
after ~15 minutes of inactivity, and the first request after that can take
up to 50 seconds — that's why you might occasionally see "Backend
unavailable — showing demo data" on first load.

## Endpoints

- `GET /stats?region=UA|World` — summary for the KPI tiles: Critical, Active Exploits, New CVE 24h, UA Alerts, High EPSS Risk, Top Vendors, By Source
- `GET /threats?source=&severity=&region=&type=&days=&limit=` — filtered list of threats
- `GET /timeline/{cve_id}` — Cyber Timeline: the full lifecycle of a threat plus an exploitation-speed verdict
- `GET /threats/{id}` — details of a single threat
- `GET /threats/{id}/explain` — AI explanation of the threat and recommendations
- `GET /health` — liveness check

## Environment Variables

```bash
DATABASE_URL= # PostgreSQL connection string (Neon)
NVD_API_KEY=
GITHUB_TOKEN=
ABUSECH_AUTH_KEY=
OTX_API_KEY=
N8N_WEBHOOK_URL= # n8n webhook for auto-publishing to Telegram
```

## Deployment (current setup)

| Component | Platform | Tier |
|---|---|---|
| Backend (FastAPI) | Render | Free |
| Database (PostgreSQL) | Neon | Free |
| Frontend (Next.js) | Vercel | Free (Hobby) |
| Data collection (cron) | GitHub Actions | Free |
| AI Automation → Telegram | n8n (self-hosted) | Free |

## Roadmap

- [x] Collectors, unified model, database, API
- [x] 10 sources (UA + World), CVSS/EPSS/exploit maturity, region toggle
- [x] Next.js dashboard
- [x] Cyber Timeline
- [x] Backend deployed on Render + Neon, frontend on Vercel
- [x] AI Automation via n8n: automatic Telegram summaries
- [ ] Verify scraper stability for SSU (depends on site layout)
- [ ] Expand AI summarization (`/threats/{id}/explain`)
- [ ] Hourly statistics in `/stats` for a real pulse line (currently a demo wave)
- [ ] Upgrade to a paid Render tier to eliminate cold starts

## Stack

Python 3.12 · FastAPI · SQLAlchemy · PostgreSQL (Neon) · GitHub Actions (cron) ·
Next.js · Recharts · n8n · Groq / SerpAPI
