<h1 align="center">NEC Asset Management System</h1>

<p align="center">
  <strong>National Electoral Commission — Somaliland</strong><br>
  <em>Habka Maareynta Hantida Komishanka Doorashooyinka Qaranka</em>
</p>

<p align="center">
  <a href="https://tournook.com"><img src="https://img.shields.io/badge/🌐_Live-tournook.com-0d6efd?style=for-the-badge" alt="Live Site"></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/DRF-3.17-CC0000?style=for-the-badge&logo=django&logoColor=white" alt="DRF">
  <img src="https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Gunicorn-23-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Gunicorn">
  <img src="https://img.shields.io/badge/Docker-29-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Traefik-3.6-24A1C1?style=for-the-badge&logo=traefikproxy&logoColor=white" alt="Traefik">
  <img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap">
  <img src="https://img.shields.io/badge/Let's_Encrypt-SSL-003A70?style=for-the-badge&logo=letsencrypt&logoColor=white" alt="SSL">
  <img src="https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="CI/CD">
  <img src="https://img.shields.io/badge/Ubuntu-24.04-E95420?style=for-the-badge&logo=ubuntu&logoColor=white" alt="Ubuntu">
</p>

---

## Table of Contents

1. [Overview](#overview)
2. [Live Deployment](#live-deployment)
3. [System Architecture](#system-architecture)
4. [Database Schema](#database-schema)
5. [Features](#features)
6. [Technology Stack](#technology-stack)
7. [Quick Start](#quick-start)
8. [REST API Reference](#rest-api-reference)
9. [Management Commands](#management-commands)
10. [Docker Operations](#docker-operations)
11. [Production Deployment](#production-deployment)
12. [Security](#security)
13. [Testing](#testing)
14. [Project Structure](#project-structure)
15. [Troubleshooting](#troubleshooting)
16. [License](#license)

---

## Overview

The NEC Asset Management System is a **production-grade, bilingual (English/Somali) web application** that digitizes and automates the National Electoral Commission's entire asset lifecycle — from procurement and registration through depreciation tracking to disposal.

It replaces manual Excel spreadsheets with a **dynamic, role-based platform** featuring real-time dashboards, automated depreciation calculations (Straight Line & Reducing Balance), inventory management with reorder alerts, and a comprehensive REST API for system integration.

### Core Capabilities

| Capability | Description |
|-----------|-------------|
| **Fixed Asset Register** | Full CRUD with auto-generated asset IDs (e.g., `ITE-DEL-0004`), serial number tracking, supplier history |
| **Depreciation Engine** | Automatic year-by-year schedules for both SL (Straight Line) and RB (Reducing Balance) methods |
| **Current Assets** | Cash, receivables, and prepayments by department and location |
| **Inventory Management** | Stock tracking with auto-calculated balance, total value, reorder alerts, and stock status indicators |
| **Reporting Suite** | Pre-built reports by category, department, status, and reorder levels with Excel export |
| **Reference Data (Lists)** | Editable dropdown catalogs — categories, departments, locations, statuses, units |
| **User Governance** | Role-based access control (Admin, Finance, User, Viewer) with department-level assignments |
| **REST API** | JWT-authenticated API with 10+ endpoints, pagination, and rate limiting |

---

## Live Deployment

| Property | Value |
|----------|-------|
| **URL** | [https://tournook.com/](https://tournook.com/) |
| **Admin Panel** | [https://tournook.com/admin/](https://tournook.com/admin/) |
| **Health Check** | [https://tournook.com/health/](https://tournook.com/health/) |
| **API Base** | `https://tournook.com/api/` |
| **SSL Certificate** | Let's Encrypt (auto-renewing via Traefik) |
| **Server** | Ubuntu 24.04 LTS, Docker 29.6.1 |
| **Reverse Proxy** | Traefik v3.6 |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     INTERNET                            │
│  https://tournook.com  ──────────────►  Port 443        │
└──────────────────────────────────┬──────────────────────┘
                                   │
                          ┌────────▼────────┐
                          │    TRAEFIK v3.6  │
                          │  (Reverse Proxy) │
                          │  • SSL Termination│
                          │  • Let's Encrypt  │
                          │  • HTTP→HTTPS     │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │  GUNICORN (3x)  │
                          │  WSGI Server    │
                          │  Port 8000      │
                          └────────┬────────┘
                                   │
                   ┌───────────────┼───────────────┐
                   │               │               │
          ┌────────▼───┐  ┌───────▼──────┐  ┌─────▼─────┐
          │ PostgreSQL │  │    Redis 7   │  │ WhiteNoise│
          │    17      │  │  (Cache)     │  │ (Static)  │
          │  (Primary)  │  │              │  │           │
          └────────────┘  └──────────────┘  └───────────┘
```

### Request Lifecycle

1. **TLS Termination**: Traefik terminates SSL, forwards `X-Forwarded-Proto: https`
2. **Gunicorn**: 3 sync workers handle Django WSGI requests
3. **Django Security Middleware**: HSTS, X-Frame-Options, CSP headers applied
4. **Authentication**: Session auth (web UI) or JWT Bearer token (API)
5. **Permission Check**: Role-based (`admin` → `finance` → `user` → `viewer`)
6. **Database**: PostgreSQL with connection pooling (`CONN_MAX_AGE=600`)
7. **Static Files**: WhiteNoise serves compressed, cache-busted static assets
8. **Caching**: Redis-backed view caching and session storage

---

## Database Schema

### Entity-Relationship Overview

```
authentication_user
    │  role, phone, department_id (FK→lists_department)
    │
    ├── fixed_assets_fixedasset (created_by, updated_by, assigned_to)
    │       │  asset_id (auto), asset_name, purchase_cost, useful_life
    │       │  depreciation_method (SL|RB), salvage_value, condition
    │       │  FK: category, department, location, status
    │       │
    │       └── fixed_assets_depreciationschedule (CASCADE)
    │              year_number, opening_nbv, annual_depreciation
    │              accumulated_depreciation, closing_nbv
    │
    ├── current_assets_currentasset (created_by, updated_by)
    │       asset_id (auto), description, value, date_recorded
    │       FK: category, department, location, status
    │
    ├── inventory_inventoryitem (created_by, updated_by)
    │       item_code (auto), description, opening_stock
    │       received_qty, issued_qty, unit_cost, reorder_level
    │       FK: category, location, unit
    │
    └── lists_* (reference data)
            Category, Department, Location, Status, Unit
```

### Table Inventory (19 tables)

| Schema | Table | Columns | Purpose |
|--------|-------|---------|---------|
| `authentication` | `user` | 14 | Custom User model (AbstractUser + role, phone, department) |
| `fixed_assets` | `fixedasset` | 22 | Fixed asset register with auto-depreciation |
| `fixed_assets` | `depreciationschedule` | 9 | Year-by-year depreciation projections |
| `current_assets` | `currentasset` | 14 | Cash, receivables, prepayments |
| `inventory` | `inventoryitem` | 16 | Stock items with balance tracking |
| `lists` | `category` | 7 | Asset categories with codes (BLD, VEH, ITE…) |
| `lists` | `department` | 6 | Organizational departments |
| `lists` | `location` | 6 | Physical locations |
| `lists` | `status` | 6 | Asset statuses (In Use, Damaged, Disposed…) |
| `lists` | `unit` | 6 | Measurement units |
| `auth` | `user`, `group`, `permission` | 6× | Django built-in auth framework |
| `django` | `admin_log`, `content_type`, `migrations`, `session` | 4× | Django system tables |

### Performance Indexes (8 on FixedAsset)

```sql
CREATE INDEX ON fixed_assets_fixedasset (asset_id);
CREATE INDEX ON fixed_assets_fixedasset (category_id);
CREATE INDEX ON fixed_assets_fixedasset (department_id);
CREATE INDEX ON fixed_assets_fixedasset (location_id);
CREATE INDEX ON fixed_assets_fixedasset (status_id);
CREATE INDEX ON fixed_assets_fixedasset (purchase_date);
CREATE INDEX ON fixed_assets_fixedasset (condition);
CREATE INDEX ON fixed_assets_fixedasset (assigned_to_id);
```

### Depreciation Methodology

| Method | Code | Formula | Best For |
|--------|------|---------|----------|
| **Straight Line** | SL | `(Cost - Salvage) ÷ Useful Life` | Buildings, furniture, office equipment |
| **Reducing Balance** | RB | `(NBV - Salvage) × (2 ÷ Useful Life)` | Vehicles, IT equipment, machinery |

Each asset's `save()` triggers automatic generation of year-by-year `DepreciationSchedule` entries:

```
Year 1: Opening NBV=$3,000 → Annual Dep=$600 → Closing NBV=$2,400
Year 2: Opening NBV=$2,400 → Annual Dep=$600 → Closing NBV=$1,800
...
Year 5: Opening NBV=$600  → Annual Dep=$600 → Closing NBV=$0
```

### Audit Trail

All business models include:
- `created_at` / `updated_at` — auto-timestamped
- `created_by` / `updated_by` — FK to User
- All changes logged via Django Admin's `LogEntry`

---

## Features

### Dashboard

- **8 KPI Cards**: Fixed Assets count, Purchase Cost, Accumulated Depreciation, Net Book Value, Current Assets value, Inventory value, Reorder alerts, Disposed assets
- **Depreciation Trend Chart**: Matplotlib-generated line chart with annual depreciation projections (base64-embedded PNG)
- **Category Breakdown**: Asset distribution by category with counts

### Fixed Assets

- Auto-generated Asset IDs using category code prefix (e.g., `ITE-DEL-0004`)
- Auto-generated sequential serial numbers (e.g., `NEC-00001`) when left blank
- Real-time depreciation calculator in the form — auto-computes Annual Depreciation, Accumulated Depreciation, and Net Book Value as you type
- Full CRUD with inline depreciation schedule visualization
- Supports serial numbers, suppliers, purchase dates, assigned users
- Condition tracking: New → Good → Fair → Poor → Broken
- Disposal date capture for retired assets

### Current Assets

- Track liquid assets: cash balances, receivables, prepaid expenses
- Department and location allocation
- Date-recorded field for month-end reconciliation

### Inventory

- Auto-calculated `balance_qty = opening + received - issued`
- Auto-calculated `total_value = balance_qty × unit_cost`
- Auto-calculated `stock_status`: OK, Reorder Needed, Out of Stock
- Reorder level alerts on dashboard

### Reports

| Report | Route | Description |
|--------|-------|-------------|
| Reports Home | `/reports/` | Report navigation page |
| Fixed Assets by Category | `/reports/fixed-assets/by-category/` | Cost summary per category |
| Fixed Assets by Department | `/reports/fixed-assets/by-department/` | Cost summary per department |
| Asset Status | `/reports/asset-status/` | Distribution by status |
| Inventory Summary | `/reports/inventory-summary/` | Stock levels and values |
| Reorder List | `/reports/reorder-list/` | Items below reorder threshold |

All reports support **Excel export** via `/reports/export/*` routes.

### Lists (Reference Data Management)

Admin-only interface at `/lists/` for managing:

| List | Example Values |
|------|---------------|
| Categories | Guryo & Dhismayaal (Buildings), Gaadiid (Vehicles), Qalab IT (IT Equipment)… |
| Departments | Finance, HR, Operations, Supply Chain, ICT, Security… |
| Locations | Xarunta Guud (Head Office), Xafiiska Hargeysa, Bakhaarka (Warehouse)… |
| Statuses | In Use, Under Maintenance, Idle, Damaged, Disposed |
| Units | Qalab Xafiis, Alaab Cunno, Qalab Farsamo, Kale |

### User Management

- **Admin Panel**: Full Django admin at `/admin/` — create, edit, delete users; assign roles and departments
- **Self-Service Password Change**: Users can change their own password via the "Change Password" button in the navbar or via `POST /api/auth/users/change-password/`
- **Sidebar Link**: "User Management" visible to staff users
- **Role Hierarchy**:

| Role | Web UI | API | Admin |
|------|--------|-----|-------|
| **Admin** | Full access | Full CRUD | Yes |
| **Finance** | Full access | Write on assets/inventory, read on lists | No |
| **User** | Read + limited write | Read-only | No |
| **Viewer** | Read-only | Read-only | No |

### Data Import

**Web Upload** (recommended): Click "Import Excel" in the dashboard sidebar or the button on the dashboard page. Select an `.xlsx` file and the system imports it automatically.

**CLI Import** (alternative): Excel-to-database import via management command:

```bash
docker compose exec web python manage.py import_nec_excel /app/NEC_Asset_Registration.xlsx
```

The import process:
1. Parses the **Lists** sheet → creates Categories, Departments, Locations, Statuses, Units
2. Parses the **Fixed_Assets** sheet → creates assets with auto-generated IDs and depreciation schedules
3. Skips duplicates, defaults missing required fields, handles garbage data gracefully
4. Links assets to reference data by name (Somali or English)
5. Validates file type (.xlsx only) and size (max 10 MB) on web upload

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.13 | Backend runtime |
| **Web Framework** | Django | 6.0.7 | Web app, ORM, admin, auth |
| **REST API** | Django REST Framework | 3.17.1 | API serializers, viewsets, permissions |
| **API Auth** | djangorestframework-simplejwt | 5.5.1 | JWT access/refresh token authentication |
| **Database** | PostgreSQL | 17-alpine | Primary data store |
| **Database Driver** | psycopg3 | 3.2.6 | PostgreSQL adapter (binary) |
| **Cache** | Redis | 7-alpine | Session cache, view caching |
| **WSGI Server** | Gunicorn | 23.0.0 | Production WSGI with 3 workers |
| **Static Files** | WhiteNoise | 6.12.0 | Compressed, cache-busted static serving |
| **Reverse Proxy** | Traefik | v3.6 | SSL termination, routing, Let's Encrypt |
| **Frontend** | Bootstrap 5 + Icons | 5.3.2 / 1.11.1 | Responsive UI framework |
| **Charts** | Matplotlib | 3.11.1 | Server-side chart generation (PNG) |
| **Data Processing** | Pandas | 3.0.5 | Excel import/export |
| **Excel Export** | OpenPyXL | 3.1.5 | Report generation |
| **Date Utilities** | python-dateutil | 2.9.0 | Depreciation schedule date arithmetic |
| **Containerization** | Docker + Compose | 29.6.1 / 5.2.0 | Multi-service orchestration |
| **CI/CD** | GitHub Actions | — | Automated test, build, push pipeline |

---

## Quick Start

### Prerequisites

- Docker Engine 24+ and Docker Compose v5+
- 2 GB RAM, 10 GB disk (for images and data volumes)
- Git

### 5-Minute Setup

```bash
# 1. Clone
git clone https://github.com/omartani-sudo/nec_asset_management.git
cd nec_asset_management

# 2. Configure environment
cp .env.example .env
# Edit .env — set DJANGO_SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD

# 3. Start all services
docker compose up -d

# 4. Run migrations
docker compose exec web python manage.py migrate

# 5. Create admin user
docker compose exec web python manage.py createsuperuser

# 6. (Optional) Import Excel data
docker compose exec web python manage.py import_nec_excel /app/NEC_Asset_Registration.xlsx

# 7. Open browser
open http://localhost:8000/
```

### Local Development (without Docker)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=nec_asset_management.settings.development
export DATABASE_URL=postgres://nec_user:password@localhost:5432/nec_asset_management
python manage.py migrate
python manage.py runserver
```

---

## REST API Reference

### Authentication Flow

```
POST /api/auth/login/         → { access, refresh }
  │
  ├─ Access token: 12-hour expiry, use in Authorization header
  └─ Refresh token: 7-day expiry, use at /api/auth/login/refresh/
```

### Quick Example

```bash
# 1. Login — get tokens
curl -X POST https://tournook.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "NECadmin2026!"}'

# Response:
# {"access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...", "refresh": "..."}

# 2. Use access token for API calls
curl https://tournook.com/api/fixed-assets/fixed-assets/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi..."
```

### Complete Endpoint Reference

| Method | Endpoint | Auth | Role Required | Description |
|--------|----------|------|---------------|-------------|
| POST | `/api/auth/login/` | None | — | Obtain JWT token pair |
| POST | `/api/auth/login/refresh/` | Refresh | — | Refresh access token |
| POST | `/api/auth/logout/` | Access | — | Invalidate session |
| POST | `/api/auth/users/change-password/` | Access | All auth'd | Change own password |
| GET | `/api/auth/users/` | Access | All auth'd | List users |
| POST | `/api/auth/users/` | Access | Admin | Create user |
| GET | `/api/fixed-assets/fixed-assets/` | Access | All auth'd | List fixed assets (paginated) |
| POST | `/api/fixed-assets/fixed-assets/` | Access | Finance/Admin | Create fixed asset |
| GET | `/api/fixed-assets/fixed-assets/{id}/` | Access | All auth'd | Retrieve asset detail |
| PUT | `/api/fixed-assets/fixed-assets/{id}/` | Access | Finance/Admin | Update asset |
| PATCH | `/api/fixed-assets/fixed-assets/{id}/` | Access | Finance/Admin | Partial update |
| DELETE | `/api/fixed-assets/fixed-assets/{id}/` | Access | Admin | Delete asset |
| GET | `/api/fixed-assets/depreciation-schedules/` | Access | All auth'd | List all depreciation entries |
| GET | `/api/current-assets/current-assets/` | Access | All auth'd | List current assets |
| POST | `/api/current-assets/current-assets/` | Access | Finance/Admin | Create current asset |
| GET | `/api/inventory/inventory-items/` | Access | All auth'd | List inventory items |
| POST | `/api/inventory/inventory-items/` | Access | Finance/Admin | Create inventory item |
| GET | `/api/lists/categories/` | Access | All auth'd | List categories |
| POST | `/api/lists/categories/` | Access | Admin | Create category |
| GET | `/api/lists/departments/` | Access | All auth'd | List departments |
| POST | `/api/lists/departments/` | Access | Admin | Create department |
| GET | `/api/lists/locations/` | Access | All auth'd | List locations |
| POST | `/api/lists/locations/` | Access | Admin | Create location |
| GET | `/api/lists/statuses/` | Access | All auth'd | List statuses |
| POST | `/api/lists/statuses/` | Access | Admin | Create status |
| GET | `/api/lists/units/` | Access | All auth'd | List units |
| POST | `/api/lists/units/` | Access | Admin | Create unit |

### Pagination & Rate Limiting

- **Page size**: 20 items per page (`?page=2`)
- **Anonymous**: 100 requests/day
- **Authenticated**: 1,000 requests/day

### Creating a Fixed Asset (Example)

```bash
curl -X POST https://tournook.com/api/fixed-assets/fixed-assets/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset_name": "Dell Latitude 5540",
    "category": 14,
    "department": 12,
    "location": 8,
    "status": 8,
    "purchase_date": "2026-01-15",
    "purchase_cost": "1800.00",
    "useful_life": 5,
    "salvage_value": "180.00",
    "depreciation_method": "SL",
    "condition": "new"
  }'

# Response includes auto-calculated fields:
# {"asset_id": "ITE-DEL-0004", "annual_depreciation": "324.00",
#  "net_book_value": "1626.14", ...}
```

---

## Management Commands

| Command | Purpose |
|---------|---------|
| `python manage.py import_nec_excel <file.xlsx>` | Bulk import from NEC Excel register — creates lists + assets + depreciation |
| `python manage.py shell` | Interactive Django shell with auto-imported models |
| `python manage.py dbshell` | Direct PostgreSQL psql session |
| `python manage.py createsuperuser` | Create admin user with role assignment |
| `python manage.py migrate` | Apply pending database migrations |
| `python manage.py showmigrations` | List migration status |
| `python manage.py collectstatic --noinput` | Collect static files for WhiteNoise |
| `python manage.py check --deploy` | Production deployment checklist |
| `python manage.py test` | Run test suite |
| `python manage.py test --verbosity=2` | Run tests with detailed output |

---

## Docker Operations

### Service Management

```bash
# Start all services (detached)
docker compose up -d

# Start specific service
docker compose up -d web db

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ destroys data)
docker compose down -v

# View logs (follow)
docker compose logs -f web

# View logs (last 100 lines)
docker compose logs --tail=100 web

# Restart a service
docker compose restart web

# Rebuild and restart
docker compose up -d --build web

# Check service health
docker compose ps
```

### Database Operations

```bash
# PostgreSQL backup
docker compose exec db pg_dump -U nec_user nec_asset_management > backup_$(date +%Y%m%d).sql

# PostgreSQL restore
docker compose exec -T db psql -U nec_user nec_asset_management < backup.sql

# Interactive psql session
docker compose exec db psql -U nec_user -d nec_asset_management

# Check database size
docker compose exec db psql -U nec_user -d nec_asset_management \
  -c "SELECT pg_database_size('nec_asset_management') / 1024 / 1024 AS size_mb;"
```

### Maintenance

```bash
# Django shell
docker compose exec web python manage.py shell

# Clear sessions
docker compose exec web python manage.py clearsessions

# Check for missing migrations
docker compose exec web python manage.py makemigrations --check --dry-run

# Verify static files
docker compose exec web python manage.py collectstatic --noinput --dry-run

# Run specific test
docker compose exec web python manage.py test tests.test_api
```

---

## Production Deployment

### Environment Variables

Copy `.env.production` to `.env` on the server and fill in all values:

```env
# Django
DJANGO_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(66))">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgres://nec_user:<secure-password>@db:5432/nec_asset_management
DB_PASSWORD=<secure-password>

# Redis
REDIS_URL=redis://:<secure-password>@redis:6379/0
REDIS_PASSWORD=<secure-password>

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@your-domain.com
EMAIL_USE_TLS=True
```

### Traefik Integration

For deployments where Traefik is the cluster reverse proxy, add to `docker-compose.yml`:

```yaml
services:
  web:
    networks:
      - default
      - traefik_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nec.rule=Host(`your-domain.com`)"
      - "traefik.http.routers.nec.entrypoints=websecure"
      - "traefik.http.routers.nec.tls.certresolver=letsencrypt"
      - "traefik.http.services.nec.loadbalancer.server.port=8000"

networks:
  traefik_network:
    external: true
```

Or use Traefik's **file-based dynamic configuration** (`dynamic.yml`) for zero-downtime updates:

```yaml
http:
  routers:
    nec:
      entryPoints:
        - websecure
      rule: "Host(`your-domain.com`)"
      tls:
        certResolver: letsencrypt
      service: nec
  services:
    nec:
      loadBalancer:
        servers:
          - url: "http://nec_asset_management:8000"
```

---

## Security

### Active Protections

| Control | Implementation | Header/Status |
|---------|---------------|---------------|
| **SSL/TLS** | Let's Encrypt via Traefik, TLS 1.3 | Valid certificate |
| **HTTP→HTTPS** | Traefik 308 Permanent Redirect | `Location: https://...` |
| **HSTS** | `SECURE_HSTS_SECONDS=31536000` | `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` |
| **Clickjacking** | `X_FRAME_OPTIONS = 'DENY'` | `X-Frame-Options: DENY` |
| **Content Sniffing** | `SECURE_CONTENT_TYPE_NOSNIFF = True` | `X-Content-Type-Options: nosniff` |
| **Referrer Policy** | `strict-origin-when-cross-origin` | `Referrer-Policy: strict-origin-when-cross-origin` |
| **CSRF** | Django CSRF middleware | Token per form + cookie |
| **Session** | HttpOnly + Secure + SameSite=Lax | 12-hour expiry |
| **API Auth** | JWT (RS256-equivalent) | 12h access / 7d refresh |
| **Password Hashing** | Django PBKDF2 (default) | Salted + iterated |
| **SQL Injection** | Django ORM parameterized queries | Prepared statements |
| **XSS** | Django template auto-escaping | Output encoding |

### Security Headers (Live Response)

```http
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: strict-origin-when-cross-origin
```

---

## Testing

### Test Suite

```bash
# All tests
python manage.py test

# Specific test module
python manage.py test tests.test_api

# With verbosity
python manage.py test --verbosity=2

# In Docker
docker compose exec web python manage.py test
```

### Test Coverage

- Health check endpoint validation
- JWT login/logout token lifecycle
- Role-based permission enforcement (admin vs user vs unauthenticated)
- Fixed asset CRUD operations with depreciation verification
- API pagination and throttling

### CI/CD Pipeline (GitHub Actions)

Runs on every push and PR to `main`:

```
1. Validate      → python manage.py check
2. Migrate       → python manage.py migrate
3. Static Check  → python manage.py collectstatic --noinput --dry-run
4. Test          → python manage.py test
5. Docker Build  → docker build .
6. Push to GHCR  → (main branch only)
```

---

## Project Structure

```
nec_asset_management/
│
├── nec_asset_management/          # Django project package
│   ├── settings/
│   │   ├── base.py                # Base settings (all environments)
│   │   ├── development.py         # Local dev overrides
│   │   ├── production.py          # Production security & perf
│   │   └── test.py                # Test-specific config
│   ├── urls.py                    # Root URL router
│   ├── wsgi.py                    # WSGI entrypoint (Gunicorn)
│   └── asgi.py                    # ASGI entrypoint (future)
│
├── authentication/                # Custom user model + auth
│   ├── models.py                  # AbstractUser + role/phone/department
│   ├── views.py                   # Login/logout views
│   ├── serializers.py             # DRF user serializer
│   ├── api_urls.py                # /api/auth/ routes
│   ├── api_views.py               # User ViewSet
│   ├── admin.py                   # Custom UserAdmin registration
│   └── migrations/
│       └── 0001_initial.py
│
├── fixed_assets/                  # Fixed asset module
│   ├── models.py                  # FixedAsset + DepreciationSchedule
│   ├── views.py                   # CRUD views + reports
│   ├── forms.py                   # Django model forms
│   ├── serializers.py             # DRF serializers
│   ├── api_urls.py                # /api/fixed-assets/ routes
│   ├── api_views.py               # Asset + Schedule ViewSets
│   ├── admin.py
│   └── migrations/
│       ├── 0001_initial.py
│       └── 0002_...indexes.py     # Performance indexes
│
├── current_assets/                # Current assets module
│   ├── models.py
│   ├── views.py, forms.py
│   ├── serializers.py, api_urls.py, api_views.py
│   └── migrations/
│
├── inventory/                     # Inventory module
│   ├── models.py                  # Auto-balance, total_value, stock_status
│   ├── views.py, forms.py
│   ├── serializers.py, api_urls.py, api_views.py
│   └── migrations/
│
├── lists/                         # Reference data module
│   ├── models.py                  # Category, Department, Location, Status, Unit
│   ├── views.py, serializers.py
│   ├── api_urls.py, api_views.py
│   └── migrations/
│       ├── 0001_initial.py
│       └── 0002_...meta_options.py  # Plural fixes
│
├── reports/                       # Reporting module
│   ├── views.py                   # Report generation + Excel export
│   └── urls.py
│
├── dashboard/                     # Home dashboard
│   ├── views.py                   # KPI aggregation + chart generation
│   └── urls.py
│
├── core/                          # Core utilities
│   ├── views.py                   # Health check endpoint
│   ├── context_processors.py      # Template context
│   └── management/commands/
│       └── import_nec_excel.py    # Excel bulk import command
│
├── templates/                     # Django templates
│   ├── base.html                  # Layout with sidebar + header
│   ├── home.html                  # Welcome page
│   ├── 403.html, 404.html, 500.html
│   ├── authentication/login.html
│   ├── dashboard/dashboard.html
│   ├── fixed_assets/              # list, detail, form, delete
│   ├── current_assets/            # list, form, delete
│   ├── inventory/                 # list, form, delete
│   ├── lists/lists.html
│   └── reports/                   # home, fixed_assets_summary, asset_status, etc.
│
├── static/                        # Static assets
│   ├── css/style.css
│   ├── js/main.js
│   └── images/nec_logo.jpg
│
├── tests/
│   ├── __init__.py
│   └── test_api.py                # API integration tests
│
├── NEC Asset registration -Final.xlsx  # Reference data source
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # Service orchestration
├── docker-entrypoint.sh           # Migration + Gunicorn startup
├── .env.example                   # Environment template
├── .env.production                # Production env template
├── requirements.txt               # Python dependencies
├── manage.py                      # Django management CLI
└── README.md                      # This file
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL status
docker compose ps db

# Check logs
docker compose logs db --tail=50

# Test connection from web
docker compose exec web python manage.py shell \
  -c "from django.db import connection; connection.ensure_connection(); print('OK')"
```

### Static Files Not Loading

```bash
# Re-collect static files
docker compose exec web python manage.py collectstatic --noinput --clear

# Verify WhiteNoise is configured
docker compose exec web python manage.py shell \
  -c "from django.conf import settings; print(settings.STORAGES['staticfiles'])"
```

### Migration Issues

```bash
# Check status
docker compose exec web python manage.py showmigrations

# Fake a migration (emergency only)
docker compose exec web python manage.py migrate --fake <app_name>

# Revert to previous migration
docker compose exec web python manage.py migrate <app_name> <migration_number>
```

### Permission Issues

```bash
# Fix file ownership in container
docker compose exec -u root web chown -R django:django /app/media
docker compose exec -u root web chmod -R 755 /app/fixed_assets/migrations
```

### SSL / Certificate Issues

```bash
# Check Traefik certificate
curl -skv https://tournook.com/ 2>&1 | grep -E "subject:|issuer:|expire"

# Force certificate renewal
docker compose -f /opt/waakuma/docker-compose.prod.yml restart traefik
```

---

## License

**Proprietary** — National Electoral Commission (NEC), Somaliland.

Unauthorized copying, distribution, or use of this software is strictly prohibited.

---

## Support

For technical issues, database administration, or feature requests:

- **Admin Panel**: [https://tournook.com/admin/](https://tournook.com/admin/)
- **API Docs**: See [REST API Reference](#rest-api-reference) above
- **Health Status**: [https://tournook.com/health/](https://tournook.com/health/)

---

<p align="center">
  <sub>Built with Python, Django, PostgreSQL, and Docker • Deployed on Ubuntu 24.04 with Traefik & Let's Encrypt</sub>
</p>
