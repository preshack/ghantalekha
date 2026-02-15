# WorkClock

**Self-hosted Employee Attendance & Payroll System**

A full-stack web application for employee clock-in/out via PIN, manager dashboard with payroll metrics, automated monthly reports, and CSV/Excel export.

---

## Features

- **PIN Clock System** — Employees clock in/out using a 4-digit PIN on a kiosk-style keypad
- **Manager Dashboard** — Real-time metrics: active employees, hours today, monthly totals, payroll cost
- **Overtime Tracking** — Automatic calculation (hours > 160/month = overtime at 1.5x rate)
- **Payroll Export** — Download CSV or Excel payroll reports
- **Email Notifications** — Managers notified on every clock-in/out + monthly payroll summary
- **Manual Adjustments** — Managers can correct attendance records with audit trail
- **Dark Mode** — Toggle with localStorage persistence
- **GPS & IP Logging** — Optional location tracking per clock event
- **Automated Monthly Reports** — Scheduled job on 1st of each month
- **Docker Ready** — 4-container stack (web, scheduler, PostgreSQL, Redis)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask 3.1 |
| Database | PostgreSQL 16 |
| Cache/Sessions | Redis 7 |
| Frontend | HTML + Tailwind CSS (CDN) |
| Auth | Session-based (Flask-Login) |
| WSGI Server | Gunicorn |
| Scheduler | APScheduler 3.x |
| Containerization | Docker + Docker Compose |

---

## Quick Start (Docker)

### 1. Clone and configure

```bash
git clone <your-repo-url> workclock
cd workclock
cp .env.example .env
# Edit .env with your SMTP credentials and a strong SECRET_KEY
```

### 2. Start all services

```bash
docker compose up --build -d
```

This starts 4 containers:
- `workclock-web` — Flask app on port 8000
- `workclock-scheduler` — Monthly report job runner
- `workclock-db` — PostgreSQL database
- `workclock-redis` — Redis for sessions & rate limiting

### 3. Initialize database & seed data

```bash
# Initialize migrations
docker compose exec web flask db init

# Generate and apply migration
docker compose exec web flask db migrate -m "Initial migration"
docker compose exec web flask db upgrade

# Seed test data (5 employees + 1 manager)
docker compose exec web flask seed
```

Or run the setup script:
```bash
bash init.sh
```

### 4. Open the app

- **Kiosk (Clock In/Out):** [http://localhost:8000](http://localhost:8000)
- **Manager Dashboard:** [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
- **Health Check:** [http://localhost:8000/api/status](http://localhost:8000/api/status)

---

## Default Credentials

### Manager Login
| Field | Value |
|-------|-------|
| Email | `manager@workclock.com` |
| Password | `manager123` |

### Employee PINs
| Name | PIN | Hourly Rate |
|------|-----|-------------|
| Alice Johnson | `1234` | $25.00/hr |
| Bob Smith | `2345` | $22.50/hr |
| Charlie Davis | `3456` | $20.00/hr |
| Diana Wilson | `4567` | $18.00/hr |
| Edward Brown | `5678` | $15.00/hr |

---

## Project Structure

```
workclock/
├── app/
│   ├── __init__.py              # App factory (create_app)
│   ├── extensions.py            # Flask extensions init
│   ├── models/                  # SQLAlchemy models
│   │   ├── employee.py          # Employee model (PIN + password auth)
│   │   ├── attendance.py        # Clock-in/out records
│   │   └── notification.py      # Email notification log
│   ├── auth/                    # Auth blueprint (manager login)
│   ├── attendance/              # Attendance blueprint (kiosk)
│   ├── dashboard/               # Dashboard blueprint (manager)
│   ├── api/                     # API blueprint (exports, health)
│   ├── services/                # Business logic layer
│   │   ├── attendance_service.py
│   │   ├── payroll_service.py
│   │   └── email_service.py
│   ├── jobs/                    # Scheduled jobs
│   │   └── monthly_report.py
│   ├── templates/               # Jinja2 HTML templates
│   ├── static/                  # CSS & JavaScript
│   ├── seeds/                   # Database seed data
│   └── utils/                   # Decorators & helpers
├── config.py                    # Configuration classes
├── wsgi.py                      # WSGI entry point
├── scheduler.py                 # Scheduler entry point
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # 4-service stack
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
└── init.sh                      # Database setup script
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key (use 32+ random chars) | `dev-secret-key...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://workclock:...@db:5432/workclock` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username/email | (empty) |
| `SMTP_PASS` | SMTP password/app password | (empty) |
| `MAIL_DEFAULT_SENDER` | From address for emails | `noreply@workclock.com` |
| `MANAGER_EMAIL` | Fallback manager email | `manager@workclock.com` |
| `OVERTIME_MONTHLY_THRESHOLD` | Hours before overtime kicks in | `160` |
| `RATELIMIT_STORAGE_URI` | Rate limit backend | `redis://redis:6379/1` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `workclock_password` |

---

## CLI Commands

```bash
# Seed database with test data
docker compose exec web flask seed

# Run database migrations
docker compose exec web flask db upgrade

# Manually trigger monthly payroll report
docker compose exec web flask run-monthly-report

# Run report for a specific month
docker compose exec web flask run-monthly-report --year 2026 --month 1
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Kiosk (PIN entry) | Public |
| POST | `/clock` | Process PIN clock-in/out | Public (rate limited) |
| GET | `/auth/login` | Manager login page | Public |
| POST | `/auth/login` | Manager login | Public |
| GET | `/auth/logout` | Logout | Authenticated |
| GET | `/dashboard/` | Manager dashboard | Manager |
| GET | `/dashboard/employee/<id>` | Employee detail | Manager |
| GET/POST | `/dashboard/adjust/<id>` | Adjust record | Manager |
| GET | `/api/export/csv?year=&month=` | Download CSV | Manager |
| GET | `/api/export/excel?year=&month=` | Download Excel | Manager |
| GET | `/api/status` | Health check | Public |

---

## Security

- **PIN hashing** — bcrypt with default work factor
- **Rate limiting** — 5 PIN attempts/minute per IP, 10 login attempts/minute
- **CSRF protection** — Flask-WTF on all forms
- **Session security** — Server-side sessions in Redis, secure cookies in production
- **Input validation** — WTForms validators on all inputs
- **Non-root Docker** — App runs as `workclock` user in container
- **Protected routes** — `@login_required` + `@manager_required` on dashboard

---

## Deployment on Oracle Cloud

1. Provision an Always Free compute instance (ARM or AMD)
2. Install Docker & Docker Compose
3. Clone the repo and configure `.env`
4. Set `SECRET_KEY` to a strong random value
5. Configure SMTP credentials for email notifications
6. Run `docker compose up -d --build`
7. Run `bash init.sh` to initialize the database
8. (Optional) Set up a reverse proxy with nginx + Let's Encrypt for HTTPS

---

## Overtime Rules

- Standard threshold: **160 hours/month** (configurable via `OVERTIME_MONTHLY_THRESHOLD`)
- Hours above threshold are flagged as overtime
- Overtime pay calculated at **1.5x** the hourly rate
- Dashboard shows regular and overtime hours/pay separately

---

## License

MIT
