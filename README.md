# UA Cyber Threat Dashboard

Агрегатор угроз кибербезопасности для Украины: собирает данные из NVD, CISA KEV
и CERT-UA, приводит к единой модели и отдаёт через REST API.

## Архитектура

```
Collectors (10 источников, см. таблицу ниже)
        ↓
   Normalizer (внутри каждого коллектора → Threat)
        ↓
   Storage (upsert с дедупликацией)  →  EPSS enrichment
        ↓
   SQLite / PostgreSQL
        ↓
   FastAPI  →  /threats?region=UA|World  /stats  /health
        ↓
   Dashboard (Next.js — следующий этап)
```

## Источники данных

| Источник | Регион | Тип | Статус |
|---|---|---|---|
| NVD | World | CVE + CVSS score | ✅ реальный API |
| CISA KEV | World | активно эксплуатируемые CVE | ✅ реальный API |
| GitHub | World | PoC-эксплойты | ✅ протестировано вживую |
| Exploit-DB | World | готовые эксплойты | ✅ рабочий CSV-фид (gitlab.com — недоступен из этой песочницы, но открыт в обычном окружении) |
| The Hacker News / BleepingComputer | World | новости | ✅ рабочий RSS |
| NCSC UK | World | официальные threat reports | ✅ рабочий RSS |
| ThreatFox (abuse.ch) | World | IOC (вредоносные IP/домены/хэши) | ✅ реальный API |
| CERT-UA | UA | предупреждения | ✅ рабочий RSS |
| Кіберполіція України | UA | новости | ⚠️ черновик-скрапер, **проверь селекторы** в `app/collectors/registry.py` |
| Держспецзв'язку (SSSCIP) | UA | новости | ⚠️ черновик-скрапер, **проверь селекторы** |
| НКЦК / СБУ | UA | — | ❌ не нашёл стабильной ленты новостей под скрапинг — пришли ссылку на конкретную страницу со списком, если знаешь такую |

Источники ⚠️ используют `GenericHTMLCollector` — они парсят HTML напрямую
(RSS/API у этих сайтов нет), поэтому хрупкие к смене вёрстки. Открой сайт
в браузере, посмотри DevTools → инспектируй карточку новости, поправь
CSS-селекторы в `registry.py`.

## Метрики риска (не только Severity-ярлык)

- **CVSS score** — насколько уязвимость технически опасна (0-10)
- **EPSS score** — вероятность реальной эксплуатации в ближайшие 30 дней (0-1), обновляется отдельным шагом в конце pipeline
- **Exploit maturity** — `PoC` (есть код на GitHub) → `Weaponized` (готовый эксплойт на Exploit-DB) → `In the wild` (в CISA KEV, то есть уже реально атакуют)

## Быстрый старт

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Собрать данные (в этой песочнице сеть к NVD/CISA/CERT-UA закрыта —
# запусти локально или из GitHub Actions, там доступ открыт)
python -m app.pipeline

# Поднять API
uvicorn app.main:app --reload
# → http://localhost:8000/docs — Swagger UI со всеми эндпоинтами
```

## Эндпоинты

- `GET /stats?region=UA|World` — сводка для плашек: Critical, Active Exploits, New CVE 24h, UA Alerts, High EPSS Risk, Top Vendors, By Source
- `GET /threats?source=&severity=&region=&type=&days=&limit=` — список угроз с фильтрами (это и есть переключатель "Украина / Мир" на фронтенде — просто параметр `region`)
- `GET /timeline/{cve_id}` — Cyber Timeline: хронология жизни угрозы (публикация → PoC → KEV) + rule-based вердикт о скорости эксплуатации
- `GET /threats/{id}` — детали одной угрозы
- `GET /health` — проверка живости

## Cyber Timeline

Склеивает записи из разных источников с одинаковым `cve_id` в хронологию:
публикация в NVD → первый PoC на GitHub → готовый эксплойт на Exploit-DB →
попадание в CISA KEV. Считает `days_to_poc` / `days_to_kev` и генерирует
rule-based вердикт о скорости эксплуатации (не AI — эвристика по времени
между событиями; на Этапе 5 это место естественно заменяется на LLM).

На фронтенде: клик по CVE-id в таблице угроз → `/timeline/{cve}`.

## Автообновление без своего сервера

`.github/workflows/collect.yml` запускает `python -m app.pipeline` по расписанию
(cron) прямо в GitHub Actions — бесплатно, без VPS. По умолчанию — раз в час,
для "раз в день" поменяй `cron: "0 * * * *"` на `cron: "0 6 * * *"`.

Два варианта хранения БД:
1. **SQLite в репозитории** (проще всего для MVP) — workflow сам коммитит
   обновлённый `data/threats.db` обратно в репо.
2. **Внешняя PostgreSQL** (Supabase/Neon free tier) — задай `DATABASE_URL` в
   GitHub Secrets, тогда шаг коммита БД пропускается автоматически.

## Быстрый старт (фронтенд)

```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
# → http://localhost:3000
```

Если бэкенд не запущен, фронтенд честно покажет баннер и демо-данные —
не упадёт с пустым экраном.

## Дорожная карта

- [x] Этап 1-3: коллекторы, единая модель, БД, API
- [x] Расширение: 10 источников (UA + World), CVSS/EPSS/exploit maturity, переключатель region
- [x] Этап 4: дашборд на Next.js — KPI-плашки, топ-вендоров, таблица угроз, UA/World toggle, пульс-линия активности
- [ ] Проверить и поправить селекторы `registry.py` для кіберполіції и SSSCIP
- [ ] Этап 5: AI-суммаризация через OpenAI API (`/threats/{id}/explain`)
- [x] Cyber Timeline: склейка published → poc_published → added_to_kev по CVE, страница /timeline/{cve} на фронтенде
- [ ] Этап 5: AI-суммаризация через OpenAI API (заменит rule-based вердикт в Cyber Timeline на LLM)
- [ ] Telegram-бот с критическими оповещениями
- [ ] Почасовая статистика в `/stats` для реальной пульс-линии (сейчас на фронте демо-волна)

## Стек

Python 3.12 · FastAPI · SQLAlchemy · SQLite/PostgreSQL · GitHub Actions (cron) ·
далее — Next.js + Recharts для фронтенда
