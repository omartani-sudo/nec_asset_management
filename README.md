# NEC Asset Management System

A comprehensive, web-based Asset Management System designed for the National Electoral Commission (NEC). This system digitizes and automates asset management, replacing manual spreadsheets with a dynamic web application.

## Features

- **Dashboard**: Real-time KPIs and depreciation trend charts
- **Fixed Assets Registration**: Full CRUD with auto-depreciation calculations (Straight Line & Reducing Balance)
- **Current Assets Management**: Track cash, receivables, and prepayments
- **Inventory Management**: Stock tracking with auto-calculated balance, reorder levels, and status
- **Reports**: Auto-generated reports by category, department, status, and reorder lists
- **Lists Management**: Editable dropdown lists (admin only)
- **Role-Based Access**: Admin, Finance, User, and Viewer roles
- **Responsive Design**: Works on desktop, tablet, and mobile

## Technology Stack

- **Backend**: Python 3.13, Django 6.0.7, Django REST Framework
- **Database**: PostgreSQL 17
- **Frontend**: Django Templates, Bootstrap 5, JavaScript
- **Reporting**: Matplotlib, OpenPyXL
- **Authentication**: Django built-in auth with custom User model
- **Server**: Gunicorn + WhiteNoise
- **Caching**: Redis
- **Containerization**: Docker & Docker Compose

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
   ```bash
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

### Static Files

WhiteNoise serves static files efficiently without requiring Nginx:

```bash
python manage.py collectstatic
```

Static files are collected to `/app/staticfiles/` in the container.

### Media Files

Media files are stored in `/app/media/` and should be persisted using Docker volumes.

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
    "timestamp": "2024-01-01T00:00:00Z"
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
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── authentication/
├── fixed_assets/
├── current_assets/
├── inventory/
├── lists/
├── reports/
├── dashboard/
├── core/
├── templates/
├── static/
├── media/
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
