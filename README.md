
# URL Shortener API

A high-performance, production-ready URL shortening service built with **FastAPI**, **SQLAlchemy 2.0**, and **PostgreSQL** (hosted on Supabase). Designed with a clean, decoupled 3-tier architecture (Routers → Services → Repositories).

---

## 🚀 Features

- **Fast & Scalable Shortening**: Generate 7-character cryptographically secure random codes (`secrets`) or supply custom aliases.
- **HTTP 307 Redirects**: Lightning-fast redirects preserving HTTP request methods.
- **Click Analytics & Tracking**: Automatically logs visitor metadata for every redirect:
  - Timestamp (UTC)
  - Referrer URL
  - Client IP address (`INET` Postgres type)
  - User-Agent header
- **Link Expiration & Soft Deactivation**:
  - Optional expiration timestamps with timezone awareness.
  - Automatically serves `410 Gone` for expired or deactivated links.
- **Collision Handling**: Automatic retry generation in the rare event of short-code collisions.
- **Robust Database Migrations**: Schema evolution tracked cleanly with **Alembic**.
- **Strict Input Validation**: Validates URLs, payload types, and timestamps with **Pydantic v2**.

---

## 🏗️ Architecture

The codebase enforces strict separation of concerns:

```
HTTP Request
     │
     ▼
[ Routers ]         app/routes/
  • HTTP routing, status codes, query/body parsing
     │
     ▼
[ Services ]        app/services/
  • Business logic: collision checks, expiry calculation, redirect resolution
     │
     ▼
[ Repositories ]    app/repositories/
  • Isolated database queries (SQLAlchemy 2.0 select statements, commits)
     │
     ▼
[ Database Models ] app/db/models.py
  • Postgres relational tables (urls, clicks) via SQLAlchemy ORM
```

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (via [Supabase](https://supabase.com/))
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) & [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

## 📂 Project Structure

```text
URL_Shortener/
├── alembic/                      # Alembic migration environment
│   ├── versions/                 # Auto-generated database migration versions
│   └── env.py                    # Alembic runtime config linked to models
├── app/
│   ├── db/
│   │   ├── models.py             # SQLAlchemy ORM definitions (Url, Click)
│   │   └── session.py            # Engine, session factory & get_db dependency
│   ├── repositories/
│   │   ├── click_repository.py   # Raw DB queries for clicks table
│   │   └── url_repository.py     # Raw DB queries for urls table
│   ├── routes/
│   │   ├── redirect.py           # GET /{short_code} endpoint
│   │   ├── shorten.py            # POST /shorten endpoint
│   │   └── stats.py              # GET /{short_code}/stats endpoint
│   ├── schemas/
│   │   ├── stats.py              # Pydantic schemas for analytics
│   │   └── url.py                # Pydantic schemas for request/response validation
│   ├── services/
│   │   ├── stats_service.py      # Aggregation and analytics logic
│   │   └── url_service.py        # Code generation, expiry logic, redirect resolution
│   ├── config.py                 # App settings loaded from .env
│   └── main.py                   # FastAPI app entrypoint & router registration
├── alembic.ini                   # Alembic configuration file
├── requirements.txt              # Project dependencies
└── README.md
```

---

## 🗄️ Database Schema

### `urls` Table
| Column | Type | Attributes | Description |
|---|---|---|---|
| `id` | `BIGINT` | Primary Key, Autoincrement | Unique ID |
| `short_code` | `VARCHAR(10)` | Unique, Indexed, Not Null | Unique identifier string |
| `long_url` | `TEXT` | Not Null | Target destination URL |
| `created_at` | `TIMESTAMPTZ` | Indexed, Not Null, Default: `now()` | Creation timestamp |
| `expires_at` | `TIMESTAMPTZ` | Nullable | Expiration timestamp |
| `is_active` | `BOOLEAN` | Not Null, Default: `true` | Soft-delete status flag |

### `clicks` Table
| Column | Type | Attributes | Description |
|---|---|---|---|
| `id` | `BIGINT` | Primary Key, Autoincrement | Unique click event ID |
| `url_id` | `BIGINT` | Foreign Key (`urls.id`), On Delete Cascade | Link to parent URL |
| `clicked_at` | `TIMESTAMPTZ` | Not Null, Default: `now()` | Click timestamp |
| `referrer` | `TEXT` | Nullable | HTTP Referer header |
| `ip_address` | `INET` | Nullable | Client IP address |
| `user_agent` | `TEXT` | Nullable | Browser User-Agent header |

*Index*: Composite index on `(url_id, clicked_at)` for rapid analytics queries.

---

## 🔌 API Endpoints

### 1. Health Check
- **`GET /`**
- **Response**: `200 OK`
```json
{
  "status": "healthy"
}
```

---

### 2. Shorten URL
- **`POST /shorten`**
- **Status**: `201 Created`

**Request Body:**
```json
{
  "long_url": "https://github.com/Prabhu-Jethi",
  "custom_alias": "my-gh",          // Optional
  "expires_at": "2026-12-31T23:59:59Z" // Optional (ISO-8601 with timezone)
}
```

**Response Body:**
```json
{
  "short_code": "my-gh",
  "short_url": "http://localhost:8000/my-gh",
  "long_url": "https://github.com/Prabhu-Jethi",
  "created_at": "2026-09-17T00:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Error Responses:**
- `409 Conflict`: Custom alias is already in use.
- `422 Unprocessable Entity`: Invalid URL format or payload validation failure.

---

### 3. Redirect to Long URL
- **`GET /{short_code}`**
- **Status**: `307 Temporary Redirect`
- **Response**: Redirects browser/client to the destination `long_url` while logging visit details in the background.

**Error Responses:**
- `404 Not Found`: Short code does not exist.
- `410 Gone`: Link has expired or has been deactivated.

---

### 4. Click Analytics & Stats
- **`GET /{short_code}/stats`**
- **Status**: `200 OK`

**Response Body:**
```json
{
  "short_code": "my-gh",
  "long_url": "https://github.com/Prabhu-Jethi",
  "total_clicks": 15,
  "created_at": "2026-09-17T00:00:00Z",
  "is_active": true,
  "recent_clicks": [
    {
      "clicked_at": "2026-09-17T01:15:30Z",
      "referrer": "https://twitter.com",
      "ip_address": "127.0.0.1",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

---

## ⚙️ Local Development Setup

### 1. Prerequisites
- Python 3.10+
- Running PostgreSQL instance (or free Supabase project)

### 2. Clone and Setup Environment
```bash
git clone https://github.com/Prabhu-Jethi/Url_Shortener.git
cd Url_Shortener

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<dbname>
SUPABASE_URL=https://<your-project-id>.supabase.co
SUPABASE_PUBLISHABLE_KEY=your_publishable_key
SUPABASE_SECRET_KEY=your_secret_key
SUPABASE_JWKS_URL=https://<your-project-id>.supabase.co/auth/v1/.well-known/jwks.json
```

### 4. Run Migrations
Apply database schema migrations using Alembic:
```bash
alembic upgrade head
```

### 5. Start the Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

Open your browser and navigate to:
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc alternative**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing

You can verify all endpoints using curl or Postman:

```bash
# 1. Shorten URL
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"long_url": "https://github.com"}'

# 2. Test Redirect (without following)
curl -v http://localhost:8000/<short_code>

# 3. View Analytics
curl http://localhost:8000/<short_code>/stats
```

---

## 📄 License
MIT License. Feel free to use and adapt this project!