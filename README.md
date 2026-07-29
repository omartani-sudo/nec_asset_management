# NEC Asset Management System

A comprehensive, production-ready Asset Management System designed for the National Electoral Commission (NEC). This system digitizes and automates asset management, replacing manual spreadsheets with a dynamic web application and REST API.

## Features

- **Dashboard**: Real-time KPIs and depreciation trend charts
- **Fixed Assets Registration**: Full CRUD with auto-depreciation calculations (Straight Line & Reducing Balance)
- **Current Assets Management**: Track cash, receivables, and prepayments
- **Inventory Management**: Stock tracking with auto-calculated balance, reorder levels, and status
- **Reports**: Auto-generated reports by category, department, status, and reorder lists
- **Lists Management**: Editable dropdown lists (admin only)
- **Role-Based Access**: Admin, Finance, User, and Viewer roles
- **REST API**: Full CRUD API with JWT authentication and role-based permissions
- **Responsive Design**: Works on desktop, tablet, and mobile

## Technology Stack

- **Backend**: Python 3.13, Django 6.0.7, Django REST Framework
- **API Auth**: JWT via `djangorestframework-simplejwt`
- **Database**: PostgreSQL 17
- **Frontend**: Django Templates, Bootstrap 5, JavaScript
- **Reporting**: Matplotlib, OpenPyXL
- **Authentication**: Django built-in auth with custom User model
- **Server**: Gunicorn + WhiteNoise
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

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

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your settings:**
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=False
   DATABASE_URL=postgres://nec_user:nec_secure_pass@db:5432/nec_asset_management
   REDIS_URL=redis://redis:6379/0
   ```

4. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

5. **Run migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

7. **Access the application:**
   - Open browser to `http://localhost:8000/`
   - Log in with superuser credentials

## REST API

The application exposes a full REST API under `/api/`. All API endpoints require authentication unless noted.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Obtain JWT access/refresh tokens |
| POST | `/api/auth/login/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Logout current session |

### Example: Login

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

### Using the API

Include the access token in the `Authorization` header:

```bash
curl http://localhost:8000/api/fixed-assets/fixed-assets/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi..."
```

### Endpoints

| Method | Endpoint | Access |
|--------|----------|--------|
| GET/POST | `/api/auth/users/` | Admin create, all authenticated read |
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

- **Admin**: Full access to all endpoints
- **Finance**: Can create/update fixed assets, current assets, inventory items; read-only for lists
- **User**: Read-only access to assets and inventory
- **Viewer**: Read-only access to assets and inventory

### Pagination & Throttling

- Page size: 20 items per page
- Anonymous rate limit: 100 requests/day
- Authenticated rate limit: 1,000 requests/day

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

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Open Django shell
docker-compose exec web python manage.py shell
```

## Coolify Deployment

### Build Command
```bash
docker-compose build web
```

### Start Command
```bash
docker-compose up -d web
```

### Health Check URL
```
http://localhost:8000/health/
```

### Environment Variables for Coolify

Set these in Coolify's environment variables section:

```env
DJANGO_SECRET_KEY=your-production-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgres://nec_user:nec_secure_pass@db:5432/nec_asset_management
REDIS_URL=redis://redis:6379/0
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@nec.gov
EMAIL_USE_TLS=True
```

## Production Settings

### Security

- `DEBUG=False`
- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS=31536000`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- `SECURE_HSTS_PRELOAD=True`
- `X_FRAME_OPTIONS=DENY`
- `SECURE_CONTENT_TYPE_NOSNIFF=True`
- `SECURE_BROWSER_XSS_FILTER=True`
- `SECURE_REFERRER_POLICY=strict-origin-when-cross-origin`

### Static Files

WhiteNoise serves static files efficiently without requiring Nginx:

```bash
python manage.py collectstatic
```

Static files are collected to `/app/staticfiles/` in the container.

### Media Files

Media files are stored in `/app/media/` and should be persisted using Docker volumes.

## Testing

### Run Tests Locally

```bash
# Using Django test runner (requires PostgreSQL running)
python manage.py test

# Using pytest with SQLite
pytest
```

### Test Coverage

- Health check endpoint validation
- JWT login/logout flow
- Permission enforcement (admin vs user)
- CRUD operations on fixed assets

### CI/CD

GitHub Actions runs on every push and pull request to `main`:

1. **Validate**: `check`, `migrate`, `collectstatic`, `test`
2. **Docker**: Build image and verify
3. **Push**: Push to GitHub Container Registry (GHCR) on main branch

## Database

### PostgreSQL Backup

```bash
# Backup
docker-compose exec db pg_dump -U nec_user nec_asset_management > backup.sql

# Restore
docker-compose exec -T db psql -U nec_user nec_asset_management < backup.sql
```

### Media Backup

```bash
# Backup media volume
docker run --rm -v nec_asset_management_media_volume:/data -v $(pwd):/backup alpine tar cvf /backup/media_backup.tar -C /data .
```

## Health Check

The application provides a health check endpoint:

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
    "timestamp": "2026-07-29T00:00:00Z"
}
```

HTTP Status Codes:
- `200 OK`: All systems operational
- `500 Internal Server Error`: Database or migration issues

## Logging

Logs are output to stdout/stderr for Docker containers:

```bash
# View logs
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

Log levels:
- INFO: General application flow
- WARNING: Django warnings
- ERROR: Application errors

## Project Structure

```
nec_asset_management/
├── nec_asset_management/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── authentication/
│   ├── api_urls.py
│   ├── api_views.py
│   ├── serializers.py
│   ├── views.py
│   ├── models.py
│   └── urls.py
├── fixed_assets/
│   ├── api_urls.py
│   ├── api_views.py
│   ├── serializers.py
│   ├── views.py
│   ├── models.py
│   └── urls.py
├── current_assets/
│   ├── api_urls.py
│   ├── api_views.py
│   ├── serializers.py
│   ├── views.py
│   ├── models.py
│   └── urls.py
├── inventory/
│   ├── api_urls.py
│   ├── api_views.py
│   ├── serializers.py
│   ├── views.py
│   ├── models.py
│   └── urls.py
├── lists/
│   ├── api_urls.py
│   ├── api_views.py
│   ├── serializers.py
│   ├── views.py
│   ├── models.py
│   └── urls.py
├── reports/
├── dashboard/
├── core/
├── templates/
├── static/
├── media/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── requirements.txt
└── manage.py
```

## Environment Variables

See `.env.example` for all available environment variables.

### Required for Production

- `DJANGO_SECRET_KEY`: Django secret key (keep secure!)
- `DATABASE_URL`: PostgreSQL database URL
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `SECURE_SSL_REDIRECT`: Set to `True` in production
- `SESSION_COOKIE_SECURE`: Set to `True` in production
- `CSRF_COOKIE_SECURE`: Set to `True` in production
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted origins for CSRF

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check PostgreSQL logs
docker-compose logs db

# Test connection
docker-compose exec web python manage.py shell -c "from django.db import connection; print(connection.ensure_connection())"
```

### Static Files Not Loading

```bash
# Recollect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Check WhiteNoise is enabled
docker-compose exec web python manage.py shell -c "from django.conf import settings; print(settings.STATICFILES_STORAGE)"
```

### Migration Issues

```bash
# Check migration status
docker-compose exec web python manage.py showmigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Fake migrations if needed
docker-compose exec web python manage.py migrate --fake
```

### Permission Issues

```bash
# Fix media directory permissions
docker-compose exec web chown -R django:django /app/media
```

## Management Commands

```bash
# Django shell
python manage.py shell

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Check system
python manage.py check

# Show URLs
python manage.py show_urls
```

## License

Proprietary - National Electoral Commission (NEC)

## Support

For issues and questions, contact the NEC IT department.
