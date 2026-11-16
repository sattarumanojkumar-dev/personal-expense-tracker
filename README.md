# Personal Expense Tracker Web Application 💰📊

A modern, production-ready, full-stack Personal Expense Tracker built with **Python 3.12**, **Django 5.1**, **PostgreSQL**, and **Chart.js**.

Designed with **strict backend-enforced user data isolation**, mobile responsiveness, intuitive expense analytics, dynamic reporting, and phone-number-based authentication.

---

## 🌟 Key Features

1. **Authentication & Multi-User Architecture**:
   - Register and login using **phone numbers** (unique identifier, format validated, with secure PBKDF2 password hashing).
   - Strict individual user data isolation at the backend and SQL query level: Users only see, edit, delete, and report on their own expenses.
   - Profile settings to update display name and change passwords with current password verification.
   - Clean security: tamper protection prevents viewing or deleting another user's expense by manipulating URL IDs (returns `404 Not Found`).

2. **Dynamic Dashboard**:
   - **4 Live Metric Cards**: Total Expenses, This Month's Expenses, Today's Expenses, Total Number of Transactions (calculated directly via SQL aggregate queries).
   - **Recent Transactions**: Displays the latest 5 expenses with category badges and Indian Rupee (₹) amounts.
   - **Interactive Charts (Chart.js)**:
     - 6-Month Spending Trend Bar Chart.
     - Category-wise Expense Distribution Doughnut Chart.

3. **Complete Expense Management**:
   - **Add Expense**: Title, Amount (> ₹0), Category (Food, Transportation, Shopping, Education, Entertainment, Healthcare, Bills & Utilities, Travel, Other), Payment Method (Cash, UPI, Debit Card, Credit Card, Bank Transfer, Other), Expense Date, and optional Description.
   - **View All Expenses**: Professional table with pagination (10 items per page).
   - **Advanced Search & Filtering**: Filter simultaneously by keyword, category, specific date, month, and year with live summary of filtered totals.
   - **Update & Delete**: Modify existing records or safely delete with confirmation modal.

4. **Monthly Reports & Analytics**:
   - Month & Year selector.
   - Month-over-month comparisons (Net difference, percentage change, and trend direction).
   - Category-wise spending table with percentage progress bars.
   - Day-by-day spending distribution bar chart.
   - Informative ₹0 empty state for inactive months.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Django 5.1
- **Database**: PostgreSQL (Relational schema, indexed foreign keys, ANSI SQL aggregate queries)
- **Database Driver**: `psycopg2-binary`
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
- **Configuration**: `python-dotenv` for `.env` management

---

## 📂 Project Directory Structure

```text
personal_expense_tracker/
│
├── config/                     # Django project configuration
│   ├── __init__.py
│   ├── settings.py             # Settings (PostgreSQL DB, Auth, Templates, Static)
│   ├── urls.py                 # Main URL routing
│   ├── wsgi.py                 # WSGI application entry
│   └── asgi.py                 # ASGI application entry
│
├── accounts/                   # User authentication & profile app
│   ├── __init__.py
│   ├── models.py               # Custom User model (phone_number as USERNAME_FIELD)
│   ├── backends.py             # PhoneNumberBackend authentication
│   ├── forms.py                # Registration, Login, Profile & Password forms
│   ├── views.py                # Register, Login, Logout, Profile views
│   ├── urls.py                 # Auth endpoints
│   ├── admin.py                # Django Admin integration
│   └── tests.py                # Authentication unit tests
│
├── expenses/                   # Core expense management & reporting
│   ├── __init__.py
│   ├── models.py               # Expense model with SQL indexes
│   ├── forms.py                # ExpenseForm with amount validation
│   ├── views.py                # CRUD views, search, pagination, reports
│   ├── sql_queries.py          # Parameterized SQL analytical functions
│   ├── urls.py                 # Expense endpoints & chart API
│   ├── admin.py                # Admin registration
│   ├── tests.py                # Expense CRUD, SQL & data isolation tests
│   └── management/
│       └── commands/
│           └── seed_data.py    # Demo data generator (Users A, B, C & Admin)
│
├── dashboard/                  # Dashboard presentation app
│   ├── __init__.py
│   ├── views.py                # Dashboard metrics & chart context
│   ├── urls.py                 # Dashboard routing
│   └── tests.py                # Dashboard & Chart API tests
│
├── templates/                  # Jinja/Django HTML templates
│   ├── base.html               # Responsive layout with sidebar & topbar
│   ├── accounts/
│   │   ├── login.html          # Clean phone-based login page
│   │   ├── register.html       # Attractive registration page
│   │   └── profile.html        # Settings & password update page
│   ├── dashboard/
│   │   └── index.html          # Dashboard with summary cards & Chart.js
│   ├── expenses/
│   │   ├── expense_list.html   # Table, filters, pagination, search
│   │   ├── expense_form.html   # Add / Edit form
│   │   └── expense_confirm_delete.html # Confirmation dialog
│   └── reports/
│       └── monthly_reports.html# Monthly analysis & comparison charts
│
├── static/                     # Static styling and JavaScript
│   ├── css/
│   │   └── style.css           # Premium FinTech UI theme
│   └── js/
│       └── main.js             # Mobile navigation & alert dismissal
│
├── scripts/                    # Helper automation scripts
│   ├── start_postgres.ps1      # Start local PostgreSQL cluster
│   └── stop_postgres.ps1       # Stop local PostgreSQL cluster
│
├── manage.py                   # Django CLI management utility
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment variables
├── .env                        # Active environment configuration
├── docker-compose.yml          # Optional Dockerized PostgreSQL
└── README.md                   # Complete documentation
```

---

## 💻 Step-by-Step Local Setup Guide (Windows PowerShell)

Follow these exact commands in **Windows PowerShell**:

### 1. Prerequisites

- **Python 3.10+** (Python 3.12 recommended)
- **PostgreSQL 14+** (Local service or portable installation)

---

### 2. Navigate to Project Directory

```powershell
cd C:\Users\satta\.gemini\antigravity\scratch\personal_expense_tracker
```

---

### 3. Create & Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

---

### 4. Install Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. PostgreSQL Setup & Database Creation

Ensure PostgreSQL is running on port `5432`.

#### Option A: Using the Local Helper Script (Included)
If using the included portable PostgreSQL:
```powershell
.\scripts\start_postgres.ps1
```

#### Option B: Using Standard PostgreSQL CLI / Service
If PostgreSQL is installed as a Windows service:
```powershell
# Open psql or PowerShell to create database:
createdb -U postgres expense_tracker_db
```

#### Option C: Using Docker Compose
```powershell
docker-compose up -d
```

---

### 6. Environment Configuration (.env)

The `.env` file should have your PostgreSQL database credentials:

```ini
SECRET_KEY=your-secure-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=expense_tracker_db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=5432
USE_SQLITE_FOR_TESTS=False
```

---

### 7. Run Database Migrations

Apply the database schema to PostgreSQL:

```powershell
python manage.py makemigrations accounts expenses
python manage.py migrate
```

---

### 8. Seed Demo Users (Users A, B, C & Admin)

Populate sample accounts and expenses to verify multi-user data isolation:

```powershell
python manage.py seed_data
```

This creates the following test accounts:
| Role / User | Phone Number | Password | Notes |
| :--- | :--- | :--- | :--- |
| **User A** (Aarav Sharma) | `9876543201` | `Password123` | 8 transactions (₹25,599.50) |
| **User B** (Bhavya Patel) | `9876543202` | `Password123` | 4 transactions (₹4,869.00) |
| **User C** (Chetan Verma) | `9876543203` | `Password123` | 3 transactions (₹6,350.00) |
| **Administrator** | `9999999999` | `AdminPassword123` | Django Admin Superuser |

---

### 9. Run Automated Test Suite

Run all 24 automated unit tests covering registration, login, CRUD operations, user isolation, URL tampering prevention, SQL aggregations, and authentication checks:

```powershell
python manage.py test accounts expenses dashboard
```

---

### 10. Start the Development Server

```powershell
python manage.py runserver 127.0.0.1:8000
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

Log in with:
- **Phone**: `9876543201`
- **Password**: `Password123`

---

## 🧪 Verifying User Data Separation

1. Log in as **User A** (`9876543201`). Notice dashboard shows ₹25,599.50 and User A's expenses.
2. In another browser tab or private window, log in as **User B** (`9876543202`). Notice dashboard shows ₹4,869.00 and User B's separate transactions.
3. Attempting to manually navigate to an expense owned by another user (e.g. `http://127.0.0.1:8000/expenses/edit/<id_of_user_a>/` while logged in as User B) immediately results in a **404 Not Found** error.

---

## 🛡️ Security Features

- **No Plaintext Passwords**: Uses Django's PBKDF2 with SHA-256 password hashing.
- **CSRF Protection**: All POST forms include `{% csrf_token %}` tokens.
- **SQL Injection Prevention**: All SQL queries use parameterized arguments (`%s`) via `django.db.connection`. Untrusted user inputs are never concatenated.
- **Strict Server-Side Ownership**: All queries filter by `user=request.user` or `user_id = %s`.
- **Session Security**: Session tokens regenerated upon login and logout.
