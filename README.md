# Virat Tent House — Complete Event & Infrastructure Management Platform

A production-ready web application built with **Django 5+**, **Bootstrap 5**, and **Django REST Framework** designed specifically for Indian tent house and wedding decoration businesses.

The platform provides two integrated environments:
1. **Customer-Facing Public Website**: Showcases luxury German Hangar tents, royal mandap designs, packages, galleries, instant inquiry submission, and floating WhatsApp buttons.
2. **Internal Enterprise ERP System**: A complete operational command center for the business owner, managers, and staff to manage real-time inventory availability, prevent double bookings, handle dispatch/returns, generate itemized PDF quotations, track payments/expenses, and view business analytics.

---

## 🌟 Key Features

### 1. Customer-Facing Website
- **Royal Aesthetic**: Designed with a curated palette of royal maroon (`#8A1424`), festive gold (`#CFA83B`), and midnight tones, modern typography (`Cinzel` and `Outfit`), and card interactions.
- **Service Catalog**: Filter by category (Wedding Tents, Royal Mandap, Stage Decor, Lighting, Furniture, Gensets, Misting Coolers). Supports various pricing models: Fixed, Per Item, Per Day, Per Guest, Per Sq Ft, and Custom Quotations.
- **Curated Packages**: All-inclusive bundles such as the *Royal Maharaja Wedding Package*, *Vibrant Haldi & Mehndi Setup*, and *Grand Reception Package*.
- **Customer Enquiry Pipeline**: Form generates a unique reference number (`VTH-ENQ-2026-0001`), creates staff in-app notifications, and offers an instant one-click WhatsApp message link.
- **Customer Portal**: Dedicated self-service portal where customers can log in to view active bookings, download PDF quotations, and check remaining balances.
- **SEO & Social Ready**: Meta tags, Open Graph tags, dynamic sitemap (`/sitemap.xml`), and robots (`/robots.txt`).

### 2. Internal Tent House ERP & Operations
- **Role-Based Access Control (RBAC)**:
  - **Super Admin & Business Owner**: Unrestricted operational, financial, and brand configuration access.
  - **Manager**: Customer management, bookings, stock allocation, quotations, payments, and expenses.
  - **Staff / Supervisors**: Assigned events, checklists, and inventory dispatch/return.
  - **Customer**: View own bookings and download quotations.
- **Dynamic Inventory Availability & Shortage Detection**:
  - Automatically queries all overlapping confirmed bookings for a date range.
  - Prevents accidental overbooking (e.g., If warehouse has 500 chairs and 300 are booked for 20 Nov, a 250 chair request produces: `Available: 200`, `Shortage: 50` with an urgent warning).
- **Event Dispatch & Return Workflow**:
  - Tracks equipment milestones: *Prepared &rarr; Loaded &rarr; Dispatched &rarr; Delivered &rarr; Installed &rarr; Returned*.
  - Records returned items in good condition, damaged quantities, and missing quantities.
  - Automatically moves damaged equipment to maintenance and adjusts warehouse inventory counts.
- **Quotation & PDF Generation Engine**:
  - Auto-calculates subtotal, discounts, GST/tax, grand totals, and the 30% advance deposit.
  - Built-in **ReportLab PDF generator** creates downloadable estimates with business branding, terms and conditions, and signature blocks.
- **Financial & Expense Management**:
  - Tracks payments (Cash, UPI, Bank Transfer, Card) with UTR/reference IDs and auto-calculates remaining balances.
  - Categorizes business expenses (transport fuel, labour wages, decoration fabric, repairs, generator diesel).
  - Business analytics dashboard with Chart.js visualization of monthly revenue vs. expenses and bookings distribution by event type.
- **Event Schedule Calendar & Checklists**:
  - Visual timeline grouped by date with conflict alerts.
  - Custom event preparation checklists for every booking.
  - Staff assignment by role (Lead Supervisor, Electrician, Decorator, Driver).

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Django 5.1+, Django ORM
- **API**: Django REST Framework (DRF), django-filter
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Chart.js
- **PDF Generation**: ReportLab
- **Security & Storage**: WhiteNoise, python-dotenv
- **Database**: SQLite (local development) / PostgreSQL (production)
- **Deployment**: Gunicorn, WhiteNoise, Render / Railway ready

---

## 📂 Project Architecture

```
Virat Tent House/
├── accounts/               # Custom User model, roles, staff profiles & auth views
├── api/                    # Django REST Framework viewsets & serializers
├── bookings/               # Customer, Enquiry, Booking, Checklist, Calendar
├── core/                   # Home, About, Contact, ERP Dashboard, BrandConfig, Reports
├── finance/                # Quotations, Payments, Expenses, and ReportLab PDF generator
├── gallery/                # Category-based portfolio showcase
├── inventory/              # Inventory assets, dynamic overlap calculator, dispatch/return
├── services/               # Services catalog, pricing structures, curated packages
├── static/                 # Custom CSS design system, JavaScript utilities
├── templates/              # Reusable Django templates and responsive layouts
├── vth_project/            # Django root configuration and settings
├── .env.example            # Environment configuration template
├── manage.py               # Django management utility
├── Procfile                # Production deployment procfile
├── requirements.txt        # Python package dependencies
└── runtime.txt             # Python runtime version
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
Ensure Python 3.12+ and Git are installed on your machine.

### 2. Setup Virtual Environment
```bash
python -m venv .venv

# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 5. Run Database Migrations
```bash
python manage.py migrate
```

### 6. Populate Realistic Demo Data
Run the automated seed command to create realistic Indian wedding inventory, packages, bookings, payments, and demo user accounts:
```bash
python manage.py seed_demo_data
```

### 7. Launch Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Demo Login Credentials

| Role | Username | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `adminpassword123` | Full ERP & Django Admin |
| **Business Owner** | `virat_owner` | `ownerpassword123` | Full Business ERP & Brand Config |
| **Manager** | `rajesh_manager` | `managerpassword123` | Bookings, Inventory, Finance, Staff |
| **Supervisor Staff** | `mukesh_supervisor` | `staffpassword123` | Assigned Events, Dispatches, Checklists |
| **Customer** | `amit_customer` | `customerpassword123` | Customer Portal, Bookings, PDF Quotes |

---

## 🧪 Running Automated Tests

Run the full automated test suite covering authentication, permissions, inventory overlap calculations, booking balances, and PDF generation:

```bash
python manage.py test
```

---

## 🔄 End-to-End Business Workflow

```
Customer visits website
        ↓
Browses Services / Packages / Photo Gallery
        ↓
Submits Online Enquiry (Generates VTH-ENQ-2026-0001)
        ↓
Staff receives In-App Notification & Contacts Client on WhatsApp
        ↓
Manager generates itemized Quotation (VTH-QTN-2026-0001) with PDF Download
        ↓
Customer approves Quotation
        ↓
Manager converts Enquiry to Confirmed Booking (VTH-BKG-2026-0001)
        ↓
ERP checks date & physical inventory availability (Checks overlap & warns on shortage)
        ↓
Advance Payment recorded (Cash / UPI / Bank Transfer)
        ↓
Event checklist generated & Staff assigned (Supervisor, Electrician, Decorator)
        ↓
Equipment Dispatched to venue (Prepared → Loaded → Dispatched → Installed)
        ↓
Event takes place
        ↓
Inventory Returned to godown (Returned, Damaged, and Missing counts updated)
        ↓
Remaining balance payment collected
        ↓
Booking marked Completed → Automatically reflected in Net Profit reports
```

---

## 🌐 Production Deployment

The project is structured for zero-configuration deployment to **Render**, **Railway**, or any standard cloud provider:
- **Web Server**: `Gunicorn` via `Procfile`
- **Static Assets**: Automatically served with caching and compression via `WhiteNoise`
- **Database**: Set `DATABASE_URL=postgres://...` in production environment variables to switch from SQLite to PostgreSQL.

---

## 📄 License
Crafted for **Virat Tent House**. All rights reserved.
