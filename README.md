---

# 🏝️ Resort Hotel Management System

<!-- Badge row -->

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-enabled-blueviolet)](https://www.docker.com/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-orange)](https://github.com/features/actions)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)](#)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](#license)
[![Release](https://img.shields.io/badge/Release-v1.0.0-blueviolet)](#)

A complete, scalable hotel & resort management system built with **Django** — features booking, room service, staff & inventory management, analytics dashboards, and exportable reports. Designed for demo/local deployment and extensible for production.

---

## 🚀 Highlights

* Clean Django architecture with modular apps (booking, analytics, room_service, inventory, staff)
* Role-based access (Admin / Manager / Staff / Guest)
* Real-time status updates for room service & bookings
* Analytics dashboard + PDF/Excel/CSV export
* Waitlist & group booking management with dynamic pricing support
* Docker-ready for easy local/production deployment

---

## 📚 Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [API Endpoints](#api-endpoints)
* [Contributing](#contributing)
* [Support](#support)
* [License](#license)

---

## ✨ Features

### Core

* ✅ User Authentication & Role-Based Authorization
* ✅ Hotel & Room CRUD management
* ✅ Booking (Individual & Group), Waitlist & Auto-assignment
* ✅ Room Service requests with staff assignment & priority queue
* ✅ Staff management & shift allocation
* ✅ Inventory tracking & reorder alerts

### Analytics & Exports

* 📈 Revenue analysis & trend charts
* 🛏️ Occupancy tracking & forecasting
* 📊 Custom reports, scheduled reports, and ad-hoc exports (PDF / Excel / CSV)
* 📥 Data export endpoints for BI ingestion

### Booking & Room Service

* 🔁 Dynamic pricing & package deals
* 🔔 Real-time status updates for requests
* ⭐ Customer feedback & rating collection
* 🚨 Cancellation and priority handling policies

---

## 🛠️ Installation

### 1. Clone

```bash
git clone https://github.com/tashok7003/Resort-Hotel-Management-System.git
cd Resort-Hotel-Management-System
```

### 2. Virtualenv (local)

```bash
python -m venv venv
# Activate
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Environment variables

Create `.env` in project root:

```
SECRET_KEY=your_secret_key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=app_password
```

### 4. Migrate & create superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start server

```bash
python manage.py runserver
# or for Docker:
docker-compose up --build
```

---

## ▶️ Usage

* **Admin Panel:** `http://127.0.0.1:8000/admin/` — manage hotels, rooms, bookings, inventory, staff
* **Analytics Dashboard:** `http://127.0.0.1:8000/analytics/` — revenue, occupancy, and reports
* **API Root:** `http://127.0.0.1:8000/api/` — programmatic access to bookings, reports, services

---

## 📁 Project Structure (short)

```
Resort-Hotel-Management-System/
├── core/             # Django project settings
├── booking/          # Booking & waitlist app
├── analytics/        # Reports & dashboards
├── room_service/     # Room service workflows
├── inventory/        # Inventory and stock
├── staff/            # Staff management
├── templates/
├── static/
├── requirements.txt
└── manage.py
```

---

## 🔌 API Endpoints (examples)

### Analytics

* **GET** `/analytics/` — Dashboard data
* **POST** `/analytics/report/generate/` — Create a report
* **GET** `/analytics/report/<id>/` — Report details
* **GET** `/analytics/export/` — Export analytics data (CSV/XLSX/PDF)

### Booking

* **GET** `/booking/` — List bookings
* **POST** `/booking/create/` — Create booking
* **GET** `/booking/<id>/` — Booking details
* **POST** `/booking/<id>/cancel/` — Cancel booking

---

## 🧪 Tests & CI

* Unit & integration tests are included in `tests/` (run with `pytest` or `python manage.py test`)
* CI configured in `.github/workflows/ci.yml` (GitHub Actions) — runs linting, tests, and builds

---


**Suggested workflow**

```bash
git checkout -b feature/your-feature
# make changes
git commit -m "feat: add amazing feature"
git push origin feature/your-feature
# open PR
```

---

## 🆘 Support

For help, raise an issue or contact: **[ashokdevamani7003@gmail.com](mailto:ashokdevamani7003@gmail.com)**

---

## 🔖 Tags / Topics

`Django` `Hotel-Management` `Booking` `Analytics` `Room-Service` `Inventory` `Staff-Management` `Docker` `PostgreSQL` `CI` `PDF-Export`

---
