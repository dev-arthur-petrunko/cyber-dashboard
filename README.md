# UA Cyber Threat Dashboard
images/Main.png
Агрегатор загроз кібербезпеки для України: збирає дані з 10 джерел
(NVD, CISA KEV, CERT-UA, ThreatFox та інші), приводить до єдиної моделі
та віддає через REST API. Має власний дашборд на Next.js та автоматичну
розсилку зведень у Telegram через n8n.

🔗 **Демо:** [cyber-dashboard-gamma.vercel.app](https://cyber-dashboard-gamma.vercel.app)
🔗 **Репозиторій:** [github.com/dev-arthur-petrunko/cyber-dashboard](https://github.com/dev-arthur-petrunko/cyber-dashboard)

## Архітектура

```
Collectors (10 джерел, див. таблицю нижче)
↓
Normalizer (всередині кожного колектора → Threat)
↓
Storage (upsert з дедуплікацією) → EPSS enrichment
↓
PostgreSQL (Neon)
↓
FastAPI (Render) → /threats?region=UA|World /stats /health
↓
┌─────────────────────┬──────────────────────────┐
↓ ↓
Dashboard (Next.js, Vercel) n8n Webhook → AI Agent → Telegram
```

## Джерела даних

| Джерело | Регіон | Тип | Статус |
|---|---|---|---|
| NVD | Світ | CVE + CVSS score | ✅ реальний API |
| CISA KEV | Світ | активно експлуатовані CVE | ✅ реальний API |
| GitHub | Світ | PoC-експлойти | ✅ |
| Exploit-DB | Світ | готові експлойти | ✅ |
| The Hacker News / BleepingComputer | Світ | новини | ✅ RSS |
| NCSC UK | Світ | офіційні threat reports | ✅ RSS |
| ThreatFox (abuse.ch) | Світ | IOC (шкідливі IP/домени/хеші) | ✅ реальний API |
| MalwareBazaar | Світ | зразки шкідливого ПЗ | ✅ реальний API |
| AlienVault OTX | Світ | pulse-звіти | ✅ |
| CERT-UA | UA | попередження | ✅ RSS |
| Кіберполіція України | UA | новини | ✅ |
| Держспецзв'язку (SSSCIP) | UA | новини | ✅ |
| НКЦК при РНБО | UA | новини | ✅ |
| СБУ / Департамент кібербезпеки | UA | новини | ⚠️ скрапер, залежить від верстки сайту |
| Vendor RSS | UA | публікації вендорів про Україну | ✅ |

## Метрики ризику (не лише Severity-ярлик)

- **CVSS score** — наскільки вразливість технічно небезпечна (0–10)
- **EPSS score** — ймовірність реальної експлуатації в найближчі 30 днів (0–1), оновлюється окремим кроком у кінці pipeline
- **Exploit maturity** — `PoC` (є код на GitHub) → `Weaponized` (готовий експлойт на Exploit-DB) → `In the wild` (у CISA KEV, тобто вже реально атакують)

## Значення з позначкою `*` — власна оцінка (немає офіційних даних)

Якщо в таблиці значення має зірочку `*` (наприклад `7.3*` або `Microsoft*`) —
це означає, що джерело **не надало офіційних даних**, і значення розраховане
нами за тими ж принципами (`app/scoring.py`):

- **CVSS `*`** (`compute_local_score`) — власна оцінка ризику **0–10** за
  методологією, наближеною до міжнародного CVSS, коли офіційний бал відсутній
  (наприклад, NVD для частини нових CVE-2026 більше не повертає CVSS/CPE).
  Формула:
  - база за `severity`: Critical = 9.0, High = 7.5, Medium = 5.0, Low = 2.0, Unknown = 4.0
  - `+` exploit maturity: In the wild = 1.2, Weaponized = 0.8, PoC = 0.5
  - `+` EPSS (ймовірність експлуатації протягом 30 днів, 0–1): до +2.0
  - `+` критичні ключові слова в заголовку/тегах (ransomware, zero-day, APT...): +0.6
  - результат обмежується діапазоном **0–10**
- **Vendor `*`** (`extract_vendor`) — виробник визначається з тексту заголовка
  новинного запису (наприклад «Critical SharePoint RCE…» → `Microsoft*`), коли
  джерело не вказало вендора. Використовується словник відомих вендорів
  (Microsoft, Cisco, Fortinet, Palo Alto Networks, Adobe, …).

Зірочки **немає**, якщо значення офіційне і надійшло від джерела.

## IOC-стрічка

Таблиця «Останні загрози» показує лише новини, CVE та advisory.
IOC-індикатори (шкідливі IP/домени/хеші) з ThreatFox, MalwareBazaar та
AlienVault OTX винесені в окрему згорнуту секцію **«IOC-стрічка
(індикатори)»** — горизонтальна стрічка карток зі значенням індикатора,
джерелом і посиланням на оригінал. API-фільтр: `GET /threats?category=feed`
(без IOC) або `?category=ioc` (тільки індикатори).

## Що зроблено

- [x] 10 колекторів (UA + Світ), єдина модель `Threat`, дедуплікація, EPSS enrichment
- [x] REST API на FastAPI: `/threats`, `/stats`, `/timeline/{cve}`, `/health`
- [x] Дашборд на Next.js: KPI-плашки, топ вендорів, таблиця загроз, перемикач Україна/Світ
- [x] Cyber Timeline — хронологія CVE (публікація → PoC → CISA KEV) з вердиктом про швидкість експлуатації
- [x] Автозбір через GitHub Actions cron — без власного сервера під pipeline
- [x] Бекенд задеплоєний на **Render** (Python/FastAPI, free tier)
- [x] База даних — **PostgreSQL на Neon** (free tier)
- [x] Фронтенд задеплоєний на **Vercel**
- [x] **AI Automation через n8n**: після кожного запуску pipeline дані летять на n8n-webhook → AI Agent (Groq + SerpAPI для пошуку контексту по незрозумілих загрозах) аналізує зведення → форматований пост автоматично публікується в Telegram-канал

## Автоматизація: pipeline → n8n → Telegram

Після завершення кожного запуску `app/pipeline.py` (включно зі збором з усіх
джерел та EPSS enrichment) дані **автоматично надсилаються POST-запитом**
на webhook у n8n:

Що відбувається на боці n8n:
1. **Webhook** приймає JSON зі статистикою (`stats`) та списком нових загроз (`new_threats`)
2. **AI Agent** аналізує дані, обирає 3–5 найважливіших загроз (пріоритет — Critical + активна експлуатація, потім UA-регіон), для незрозумілих кампаній/малварі робить **один** пошуковий запит через SerpAPI, щоб пояснити суть і дати практичну рекомендацію
3. **Code node** форматує відповідь під Telegram: емодзі, структура, ліміт у 900 символів
4. **Telegram node** публікує готовий пост у канал

Налаштовується через `N8N_WEBHOOK_URL` (див. нижче).

## Швидкий старт (бекенд)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Зібрати дані
python -m app.pipeline

# Підняти API
uvicorn app.main:app --reload
# → http://localhost:8000/docs — Swagger UI з усіма ендпоінтами
```

## Швидкий старт (фронтенд)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=<адреса бекенда>
npm run dev
# → http://localhost:3000
```

Якщо бекенд недоступний, фронтенд чесно покаже банер і демо-дані —
не впаде з порожнім екраном.

⚠️ **Про cold start:** бекенд на Render (free tier) засинає після ~15 хв
без запитів, перший запит після сну може займати до 50 секунд — саме
тому іноді на дашборді можна побачити "Бекенд недоступний — показано
демо-дані" при першому заході.

## Ендпоінти

- `GET /stats?region=UA|World` — зведення для плашок: Critical, Active Exploits, New CVE 24h, UA Alerts, High EPSS Risk, Top Vendors, By Source
- `GET /threats?source=&severity=&region=&type=&days=&limit=` — список загроз з фільтрами
- `GET /timeline/{cve_id}` — Cyber Timeline: хронологія життя загрози + вердикт про швидкість експлуатації
- `GET /threats/{id}` — деталі однієї загрози
- `GET /threats/{id}/explain` — AI-пояснення загрози та рекомендації
- `GET /health` — перевірка живості

## Змінні середовища

```bash
DATABASE_URL= # PostgreSQL connection string (Neon)
NVD_API_KEY=
GITHUB_TOKEN=
ABUSECH_AUTH_KEY=
OTX_API_KEY=
N8N_WEBHOOK_URL= # webhook n8n для автопублікації в Telegram
```
## Розгортання (як задеплоєно зараз)

| Компонент | Платформа | Тариф |
|---|---|---|
| Backend (FastAPI) | Render | Free |
| Database (PostgreSQL) | Neon | Free |
| Frontend (Next.js) | Vercel | Free (Hobby) |
| Автозбір даних (cron) | GitHub Actions | Free |
| AI Automation → Telegram | n8n (self-hosted) | Free |

## Дорожня карта

- [x] Колектори, єдина модель, БД, API
- [x] 10 джерел (UA + Світ), CVSS/EPSS/exploit maturity, перемикач region
- [x] Дашборд на Next.js
- [x] Cyber Timeline
- [x] Деплой бекенда на Render + Neon, фронтенда на Vercel
- [x] AI Automation через n8n: автоматичні зведення в Telegram
- [ ] Перевірити стабільність скраперів для СБУ (залежить від верстки сайту)
- [ ] Розширити AI-сумаризацію (`/threats/{id}/explain`)
- [ ] Погодинна статистика в `/stats` для реальної пульс-лінії (зараз демо-хвиля)
- [ ] Upgrade на платний тариф Render для усунення cold start

## Стек

Python 3.12 · FastAPI · SQLAlchemy · PostgreSQL (Neon) · GitHub Actions (cron) ·
Next.js · Recharts · n8n · Groq / SerpAPI

