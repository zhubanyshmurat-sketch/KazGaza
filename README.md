# KazGaza — тұрғындардың өтінімдерін басқару жүйесі

Тұрғындар Telegram bot арқылы өтінім қалдырады (есептегіш ақаулары, МПИ-ге шешу,
газ шығуы туралы авариялық хабарлама), ал қызметкерлер веб-админ-панель арқылы
өтінімдерді өңдейді. Backend API, PostgreSQL база, Telegram bot және Next.js
админ-панелі бір ортақ жүйе құрайды.

## Мазмұны

1. [Архитектура](#архитектура)
2. [Жоба құрылымы](#жоба-құрылымы)
3. [Орнату](#1-орнату)
4. [Telegram Bot құру (BotFather)](#2-telegram-bot-құру-botfather)
5. [BOT_TOKEN](#3-bot_token)
6. [DATABASE_URL](#4-database_url)
7. [Миграцияларды іске қосу](#5-миграцияларды-іске-қосу)
8. [Алғашқы SUPER_ADMIN құру](#6-алғашқы-super_admin-құру)
9. [Docker іске қосу](#7-docker-іске-қосу)
10. [HTTPS/domain баптау](#8-httpsdomain-баптау)
11. [Production deployment](#9-production-deployment)
12. [Тестілеу](#тестілеу)
13. [API шолу](#api-шолу)

---

## Архитектура

```
Тұрғын → Telegram Bot (aiogram 3) → Backend API (FastAPI) → PostgreSQL
                                            │                      ▲
                                            ▼                      │
                                    Admin Dashboard (Next.js) ──────┘
```

- **Backend API** — жалғыз орталық API. Telegram bot та, admin dashboard та
  тек осы API арқылы деректермен жұмыс істейді.
- Statustar өзгергенде backend Telegram Bot API-ге тікелей хабарлама
  жібереді (`BOT_TOKEN` арқылы) — жеке bot қызметін тоқтатпайды.
- Dashboard-та real-time жаңарту WebSocket (`/ws/dashboard`) арқылы жүреді.
- Фотосуреттер backend арқылы жүктеліп, валидацияланып (нақты MIME/өлшем
  тексерісі), диск köлемінде сақталады (`storage/uploads`), nginx арқылы
  беріледі.

Стек:

| Қабат | Технология |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2 |
| Telegram Bot | aiogram 3.x, Redis (FSM storage) |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Radix UI (shadcn стилінде) |
| DB | PostgreSQL 16 |
| Deployment | Docker, Docker Compose, Nginx |

## Жоба құрылымы

```
/apps
  /backend        — FastAPI REST API (models, schemas, services, repositories, api, auth)
  /telegram-bot   — aiogram 3 bot (handlers, keyboards, states, middlewares, services)
  /admin-web      — Next.js admin dashboard
/packages
  /shared/python  — backend мен bot арасында ортақ enum-дар (kazgaza_shared)
/docker
  /nginx          — reverse proxy config
/docs
docker-compose.yml
.env.example
```

---

## 1. Орнату

Талаптар: Docker + Docker Compose plugin (production үшін), немесе жергілікті
дамыту үшін Python 3.12+ және Node.js 20+.

```bash
git clone <repo-url> kazgaza
cd kazgaza
cp .env.example .env
```

`.env` файлын өз мәндеріңізбен толтырыңыз (келесі бөлімдерде түсіндіріледі).

## 2. Telegram Bot құру (BotFather)

1. Telegram-да [@BotFather](https://t.me/BotFather) ашыңыз.
2. `/newbot` командасын жіберіңіз.
3. Bot атауын және username-ін енгізіңіз (username `bot` деп аяқталуы керек,
   мысалы `KazGazaSupportBot`).
4. BotFather сізге токен береді, мысалы:
   `123456789:AAExampleTelegramBotTokenReplaceMe`.
5. Қаласаңыз, `/setdescription`, `/setuserpic` арқылы bot профилін
   толтырыңыз.

## 3. BOT_TOKEN

Алынған токенді `.env` файлындағы `BOT_TOKEN` айнымалысына қойыңыз:

```
BOT_TOKEN=123456789:AAExampleTelegramBotTokenReplaceMe
```

Сондай-ақ `BOT_INTERNAL_TOKEN` мәнін кездейсоқ мәнмен толтырыңыз — бұл
bot қызметі мен backend-тің `/bot/*` endpoint-тері арасындағы ортақ құпия:

```bash
openssl rand -hex 32
```

## 4. DATABASE_URL

Docker Compose қолданғанда `DATABASE_URL` автоматты түрде
`POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` негізінде құрылады —
тек сол үш айнымалыны толтыру жеткілікті.

Backend-ті Docker-сыз жергілікті іске қосу үшін (мысалы, тестілеу/дамыту):

```
DATABASE_URL=postgresql+asyncpg://kazgaza:your-password@localhost:5432/kazgaza
```

## 5. Миграцияларды іске қосу

Docker Compose қолданғанда backend контейнері іске қосылған сайын
миграцияларды автоматты орындайды (`entrypoint.sh` → `alembic upgrade head`).

Қолмен орындау (жергілікті даму ортасында):

```bash
cd apps/backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

## 6. Алғашқы SUPER_ADMIN құру

Docker Compose ортасында:

```bash
docker compose exec backend python -m scripts.create_superadmin \
  --name "Админ" --email admin@kazgaza.kz --password "StrongPassword123"
```

Жергілікті ортада (venv белсенді болғанда):

```bash
cd apps/backend
python -m scripts.create_superadmin --name "Админ" --email admin@kazgaza.kz --password "StrongPassword123"
```

Осыдан кейін admin-панельге осы email/құпия сөзбен кіре аласыз.

## 7. Docker іске қосу

```bash
docker compose build
docker compose up -d
docker compose logs -f backend bot frontend
```

Қызметтер:

- Admin dashboard: `http://localhost` (nginx арқылы)
- Backend API: `http://localhost/api/v1`
- Backend health-check: `http://localhost/api/v1/../health` немесе контейнер
  ішінен `http://backend:8000/health`

Тоқтату:

```bash
docker compose down
```

Деректерді (Postgres volume) жоймай тоқтату — жоғарыдағы команда жеткілікті;
volume-дерді толық жою үшін: `docker compose down -v` (⚠️ барлық деректі жояды).

## 8. HTTPS/domain баптау

1. Домен атауын серверге бағыттаңыз (A/AAAA жазба).
2. `.env` файлында `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`,
   `NEXT_PUBLIC_WS_URL`, `NEXT_PUBLIC_MEDIA_URL` мәндерін нақты доменмен
   ауыстырыңыз (мысалы `https://kazgaza.example.kz`).
3. TLS сертификатын алыңыз, мысалы Let's Encrypt/certbot арқылы:

   ```bash
   sudo certbot certonly --standalone -d your-domain.kz
   cp /etc/letsencrypt/live/your-domain.kz/fullchain.pem docker/nginx/certs/
   cp /etc/letsencrypt/live/your-domain.kz/privkey.pem docker/nginx/certs/
   ```

4. `docker/nginx/nginx.conf` файлындағы HTTPS server блогының
   түсініктемесін алып тастап, `server_name` мәнін өз доменіңізге
   өзгертіңіз, сосын 80-портты 443-ке redirect ететін блокты іске
   қосыңыз.
5. `docker compose restart nginx frontend` (frontend-ті қайта build ету
   қажет, себебі `NEXT_PUBLIC_*` айнымалылары build-time-та ендіріледі):

   ```bash
   docker compose build frontend
   docker compose up -d
   ```

## 9. Production deployment

- `.env` ішіндегі барлық `change-me` мәндерін ауыстырыңыз, әсіресе
  `SECRET_KEY`, `POSTGRES_PASSWORD`, `BOT_INTERNAL_TOKEN`.
- `COOKIE_SECURE=true` қалдырыңыз (тек HTTPS арқылы cookie жіберіледі).
- `DEBUG=false` қалдырыңыз (API docs өшірілген болады).
- Postgres volume-ін тұрақты backup-қа қосыңыз
  (`pg_dump` cron тапсырмасы ұсынылады).
- `storage_uploads` volume-ін де backup жоспарына қосыңыз (фотосуреттер).
- Nginx/Let's Encrypt сертификатын автоматты жаңарту үшін `certbot renew`
  cron тапсырмасын орнатыңыз.
- Логтарды орталықтандыру үшін `docker compose logs` орнына production-да
  сыртқы log driver (мысалы, Loki/CloudWatch) қосу ұсынылады.

---

## Тестілеу

### Backend

```bash
cd apps/backend
source .venv/bin/activate
pip install -r requirements.txt -r tests/requirements-test.txt
pytest -q
```

Критикалық сценарийлер қамтылған: авторизация/JWT, RBAC (SUPER_ADMIN /
DISPATCHER / OPERATOR), өтінім құру (барлық 3 түрі), міндетті фото/геолокация
валидациясы, GAS_LEAK → CRITICAL приоритет, статус өзгерту + Telegram
хабарландыру, тарих логы, дербес шот форматын тексеру, файл/сурет
валидациясы (MIME sniff, өлшем шегі).

### Telegram Bot

```bash
cd apps/telegram-bot
source .venv/bin/activate
pip install -r requirements.txt -r tests/requirements-test.txt
pytest -q
```

FSM интеграциялық тестері (aiogram `Dispatcher.feed_update` арқылы, желіге
шықпай) толық сценарийлерді тексереді: /start → дербес шот → растау →
өтінім түрін таңдау → фото → геолокация → растау → жіберу — үш өтінім
түрінің әрқайсысы үшін, сонымен қатар бас тарту/өзгерту/негізгі мәзір
үзу сценарийлері.

### Frontend

```bash
cd apps/admin-web
npm install
npm run build
```

---

## API шолу

Толық endpoint тізімі (барлығы `/api/v1` префиксімен):

| Endpoint | Сипаттама |
|---|---|
| `POST /auth/login` | Кіру (JWT cookie + CSRF token) |
| `POST /auth/refresh` | Access token жаңарту |
| `POST /auth/logout` | Шығу |
| `GET /auth/me` | Ағымдағы admin |
| `GET /applications` | Тізім (сүзгі/іздеу/pagination/sort) |
| `GET /applications/{id}` | Толық ақпарат |
| `PATCH /applications/{id}` | Жалпы өзгерту (комментарий, приоритет) |
| `PATCH /applications/{id}/status` | Статус өзгерту (+ Telegram хабарландыру) |
| `PATCH /applications/{id}/assign` | Орындаушы тағайындау |
| `POST /applications/{id}/comments` | Ішкі комментарий қосу |
| `GET /applications/{id}/history` | Өзгерістер тарихы |
| `GET /applications/export` | CSV/XLSX экспорт |
| `GET /dashboard/stats` | Dashboard статистикасы |
| `GET /dashboard/report` | Сүзгіленген есеп (орташа өңдеу уақыты) |
| `GET /admins`, `POST /admins`, `PATCH /admins/{id}` | Қызметкерлер |
| `GET /settings`, `PATCH /settings` | Жүйе баптаулары |
| `GET /application-types` | Өтінім түрлерінің тізімі |
| `WS /ws/dashboard` | Real-time жаңартулар |
| `POST /bot/users/register`, `POST /bot/applications`, `GET /bot/applications/mine`, `GET /bot/settings/public` | Bot-тың ішкі API-і (`X-Bot-Secret` header қажет) |

Толық Pydantic схемалары `apps/backend/app/schemas/` ішінде.

---

## Қауіпсіздік

- Құпия сөздер — bcrypt hash.
- Авторизация — httpOnly JWT cookie (access + refresh) + double-submit CSRF
  token (cookie-негізделген авторизацияға сай).
- RBAC — `SUPER_ADMIN` / `DISPATCHER` / `OPERATOR` рөлдері әр endpoint-те
  тексеріледі.
- Rate limiting — `slowapi` арқылы (login, bot endpoint-тер бөлек шектеулі).
- Файл жүктеу — тек нақты сурет мазмұны (Pillow арқылы MIME sniff),
  өлшем шегі, кеңейтім клиенттен алынбайды.
- Барлық құпиялар (`BOT_TOKEN`, `SECRET_KEY`, DB паролі) тек environment
  variables арқылы беріледі, git-ке ешқашан commit етілмейді
  (`.env` — `.gitignore`-де).
