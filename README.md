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
- **Database**: SQLite (development), easily upgradeable to PostgreSQL
- **Frontend**: Django Templates, Bootstrap 5, JavaScript
- **Reporting**: Matplotlib, ReportLab, WeasyPrint
- **Authentication**: Django built-in auth with custom User model

## Setup Instructions

### Prerequisites

- Python 3.13+
- pip
- A modern web browser

### Installation

1. **Clone or extract the project** to your desired directory.

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** (admin):
   ```bash
   python manage.py createsuperuser
   # Follow prompts. Set role to 'admin'.
   ```
   Or use the quick script:
   ```bash
   python manage.py shell -c "from authentication.models import User; User.objects.create_superuser('admin', 'admin@nec.gov', 'admin123', role='admin')"
   ```

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the application**:
   - Open your browser to `http://127.0.0.1:8000/`
   - Log in with the superuser credentials
   - Or access the Django admin panel at `http://127.0.0.1:8000/admin/`

## Project Structure

```
nec_asset_management/
├── nec_asset_management/       # Project package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── authentication/             # Custom User model and auth views
├── fixed_assets/               # Fixed Assets module
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── current_assets/             # Current Assets module
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── inventory/                  # Inventory module
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── templates/
├── lists/                      # Standard dropdown lists
│   ├── models.py
│   ├── views.py
│   └── templates/
├── reports/                    # Reporting module
│   ├── views.py
│   └── templates/
├── dashboard/                  # Dashboard module
│   ├── views.py
│   └── templates/
├── core/                       # Core functionality
│   ├── views.py
│   └── context_processors.py
├── templates/
│   └── base.html               # Base template with sidebar nav
├── static/
│   ├── css/
│   └── js/
└── manage.py
```

## Core Calculations

### Depreciation - Straight Line
```
Annual Depreciation = (Purchase Cost - Salvage Value) / Useful Life
Accumulated Depreciation = Annual Depreciation × Years Elapsed
Net Book Value = Purchase Cost - Accumulated Depreciation
```

### Depreciation - Reducing Balance
```
Year 1 Depreciation = (Purchase Cost - Salvage Value) × (2 / Useful Life)
Subsequent Years = Applied to remaining Net Book Value
```

### Inventory
```
Balance Qty = Opening Stock + Received Qty - Issued Qty
Total Value = Balance Qty × Unit Cost
Stock Status:
  - "Out of Stock" if Balance = 0
  - "Reorder Needed" if Balance <= Reorder Level and Balance > 0
  - "OK" if Balance > Reorder Level
```

## User Roles

| Role | Permissions |
|------|-------------|
| Admin | Full access, can manage Lists |
| Finance | Can add/edit assets, view reports |
| User | Can add/edit assets, view reports |
| Viewer | Read-only access |

## Database Models

- **User** (authentication): Extends AbstractUser with role, phone, department
- **Category, Department, Location, Status, Unit** (lists): Standardized dropdown values
- **FixedAsset**: Core fixed asset data with depreciation methods
- **DepreciationSchedule**: 10-year depreciation schedule per asset
- **CurrentAsset**: Current assets tracking
- **InventoryItem**: Inventory with auto-calculated fields

## Accessing the Application

After starting the server, you can access the application using:

- **Local:** `https://127.0.0.1:8000/`
- **By Computer Name:** `https://DESKTOP-25CJHGD:8000/`
- **By IP Address:** `https://192.169.169.44:8000/`

Other devices on the same network can access it using:
- `https://DESKTOP-25CJHGD:8000/` (preferred)
- `https://192.169.169.44:8000/` (alternative)

## Management Commands

```bash
python manage.py createsuperuser    # Create admin user
python manage.py shell               # Open Django shell for data operations
python manage.py runserver           # Start development server
python manage.py collectstatic       # Collect static files (production)
```

## Notes

- The system uses SQLite by default for easy deployment. To switch to PostgreSQL, update `DATABASES` in `settings.py`.
- Rotating the secret key is recommended for production.
- The dashboard generates Matplotlib charts on-the-fly as base64 images.

## Changing Network / IP Address

If your local IP address changes (e.g., different WiFi/Ethernet), update these files:

1. **`nec_asset_management/settings.py`**: Update `ALLOWED_HOSTS` with your new IP and keep the computer name
2. **Regenerate SSL certificates**:
   ```bash
   mkcert 192.169.169.44 localhost 127.0.0.1 DESKTOP-25CJHGD
   ```
   Replace `192.169.169.44` and `DESKTOP-25CJHGD` with your actual IP and computer name.
3. **Restart the server**:
   ```bash
   python manage.py runserver_plus 0.0.0.0:8000 --cert-file "192.169.169.44+3.pem" --key-file "192.169.169.44+3-key.pem"
   ```
4. **Reinstall certificate on mobile devices** if using HTTPS

## Troubleshooting

- **"ModuleNotFoundError"**: Ensure all apps are in `INSTALLED_APPS` and migrations are applied.
- **"ImproperlyConfigured"**: Verify `DATABASES` settings in `settings.py`.
- **"No module named 'django' "**: Install requirements with `pip install -r requirements.txt`.
