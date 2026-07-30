# NEC Asset Management System

A comprehensive, production-ready Asset Management System designed for the National Electoral Commission (NEC). This system digitizes and automates asset management, replacing manual spreadsheets with a dynamic web application and REST API.

**Live deployment:** [https://tournook.com/](https://tournook.com/)

---

## Features

### Core Modules
- **Dashboard**: Real-time KPIs, depreciation trend charts, and asset summary statistics
- **Fixed Assets**: Full CRUD with auto-generated asset IDs (e.g., `ITE-DEL-0004`), auto-depreciation calculations (Straight Line & Reducing Balance), depreciation schedules
- **Current Assets**: Track cash, receivables, and prepayments with departmental allocation
- **Inventory**: Stock tracking with auto-calculated balance, total value, reorder alerts, and stock status
- **Reports**: Auto-generated reports by category, department, status, and reorder lists with Excel export
- **Lists (Reference Data)**: Editable dropdown lists for categories, departments, locations, statuses, and units (admin only)

### User Management
- **Role-Based Access**: Admin, Finance, User, and Viewer roles with granular permissions
- **Admin Panel**: Django admin at `/admin/` for user CRUD, role assignment, and full data management
- **Sidebar Access**: "User Management" link for staff users

### REST API
- Full CRUD API under `/api/` with JWT authentication
- Pagination (20 items/page), throttling (100/day anonymous, 1,000/day authenticated)
- 10+ endpoints covering auth, fixed assets, current assets, inventory, and lists

### Data Import
- **Excel Import**: Management command `import_nec_excel` for bulk importing NEC asset registers
- Auto-generates asset IDs, depreciation schedules, and links reference data

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.13, Django 6.0.7, Django REST Framework |
| API Auth | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL 17 |
| Frontend | Django Templates, Bootstrap 5, Bootstrap Icons |
| Reporting | Matplotlib, OpenPyXL, Pandas |
| Server | Gunicorn + WhiteNoise |
| Caching | Redis 7 |
| Reverse Proxy | Traefik v3.6 with Let's Encrypt SSL |
| Containerization | Docker & Docker Compose |
| CI/CD | GitHub Actions |

---

## Database Schema

19 tables across 7 Django apps:

| App | Tables | Key Models |
|-----|--------|-----------|
| `authentication` | 1 | Custom User with roles, phone, department FK |
| `fixed_assets` | 2 | FixedAsset (22 columns), DepreciationSchedule |
| `current_assets` | 1 | CurrentAsset with category/department/location FKs |
| `inventory` | 1 | InventoryItem with auto-balance and stock status |
| `lists` | 5 | Category, Department, Location, Status, Unit |
| `auth` (Django) | 6 | Groups, Permissions, Sessions, Admin log |

**Indexes:** 8 indexes on FixedAsset for query performance (asset_id, category, department, location, status, purchase_date, condition, assigned_to).

**Depreciation:** Auto-generated year-by-year schedules with opening NBV, annual depreciation, accumulated depreciation, and closing NBV for both Straight Line (SL) and Reducing Balance (RB) methods.

**Audit Trail:** All models include `created_at`, `updated_at`, `created_by`, `updated_by` fields.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.13+ (for local development without Docker)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/omartani-sudo/nec_asset_management.git
   cd nec_asset_management
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations & create superuser:**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Import Excel data (optional):**
   ```bash
   docker-compose exec web python manage.py import_nec_excel /app/NEC_Asset_Registration.xlsx
   ```

6. **Access the application:**
   - App: `http://localhost:8000/`
   - Admin: `http://localhost:8000/admin/`

---

## REST API

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Obtain JWT access/refresh tokens |
| POST | `/api/auth/login/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Logout current session |

**Example:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
}
```

### Endpoints

| Method | Endpoint | Access |
|--------|----------|--------|
| GET/POST | `/api/auth/users/` | Admin write, all authenticated read |
| GET/POST | `/api/fixed-assets/fixed-assets/` | Finance/Admin write, all authenticated read |
| GET | `/api/fixed-assets/depreciation-schedules/` | All authenticated read |
| GET/POST | `/api/current-assets/current-assets/` | Finance/Admin write, all authenticated read |
| GET/POST | `/api/inventory/inventory-items/` | Finance/Admin write, all authenticated read |
| GET/POST | `/api/lists/categories/` | Admin write, all authenticated read |
| GET/POST | `/api/lists/departments/` | Admin write, all authenticated read |
| GET/POST | `/api/lists/locations/` | Admin write, all authenticated read |
| GET/POST | `/api/lists/statuses/` | Admin write, all authenticated read |
| GET/POST | `/api/lists/units/` | Admin write, all authenticated read |

### API Permissions

| Role | Permissions |
|------|------------|
| **Admin** | Full access to all endpoints |
| **Finance** | Create/update fixed assets, current assets, inventory; read-only for lists |
| **User** | Read-only access to assets and inventory |
| **Viewer** | Read-only access to assets and inventory |

---

## Management Commands

| Command | Description |
|---------|-------------|
| `python manage.py import_nec_excel <file.xlsx>` | Import assets & lists from NEC Excel register |
| `python manage.py shell` | Django interactive shell |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py collectstatic --noinput` | Collect static files |

---

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Import Excel data
docker-compose exec web python manage.py import_nec_excel /app/NEC_Asset_Registration.xlsx

# Database backup
docker-compose exec db pg_dump -U nec_user nec_asset_management > backup.sql

# Database restore
docker-compose exec -T db psql -U nec_user nec_asset_management < backup.sql
```

---

## Deployment

### Production Environment Variables

```env
DJANGO_SECRET_KEY=your-production-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgres://nec_user:password@db:5432/nec_asset_management
REDIS_URL=redis://:password@redis:6379/0
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
CSRF_TRUSTED_ORIGINS=https://your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
```

### Security Features

| Feature | Status |
|---------|--------|
| SSL/TLS (Let's Encrypt) | ✅ |
| HTTP→HTTPS Redirect | ✅ |
| HSTS (max-age=31536000) | ✅ |
| X-Frame-Options: DENY | ✅ |
| X-Content-Type-Options: nosniff | ✅ |
| Referrer-Policy | ✅ strict-origin-when-cross-origin |
| CSRF Protection | ✅ |
| Session Cookie Secure + HttpOnly | ✅ |
| JWT Token Auth | ✅ |

---

## Project Structure

```
nec_asset_management/
├── nec_asset_management/     # Django project settings
│   └── settings/
│       ├── base.py           # Base settings
│       ├── development.py    # Dev overrides
│       ├── production.py     # Production overrides
│       └── test.py           # Test overrides
├── authentication/           # Custom user model & auth views
├── fixed_assets/             # Fixed asset CRUD + depreciation
├── current_assets/           # Current asset tracking
├── inventory/                # Inventory management
├── lists/                    # Reference data (categories, etc.)
├── reports/                  # Auto-generated reports
├── dashboard/                # KPI dashboard
├── core/                     # Health check, context processors
│   └── management/commands/  # Custom management commands
├── templates/                # Django templates
├── static/                   # CSS, JS, images
├── tests/                    # Test suite
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml        # Docker Compose config
├── docker-entrypoint.sh      # Container entrypoint
└── requirements.txt          # Python dependencies
```

---

## Health Check

```
GET /health/
```

Response:
```json
{
    "status": "ok",
    "message": "All systems operational",
    "database": "connected",
    "migrations": "applied",
    "timestamp": "2026-07-30T00:00:00Z"
}
```

---

## License

Proprietary — National Electoral Commission (NEC)

## Support

For issues and questions, contact the NEC IT department.
