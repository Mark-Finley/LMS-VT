# Excelsior Laboratory Management System (LMS)

A robust, modern web-based Diagnostic Laboratory Information Management System (LIMS) designed for medical clinics, private diagnostic laboratories, and hospital networks. Built with Django, MySQL, Alpine.js, and Tailwind CSS.

---

## 🌟 Key Features & Modules

### 1. Reception & Patient Registration
- Swift registration of patient demographics.
- Walk-in and referral-based encounter intake.
- Auto-generated unique digital Requisition Numbers.

### 2. Billing, Cashier & Invoicing
- Localized pricing in **Ghana Cedis (GH₵)**.
- Invoice generation, payment recording, and balance tracking.
- Printable billing receipts.

### 3. Phlebotomy & Specimen Tracking
- Multi-specimen type selections (Whole Blood, Serum, Plasma, Urine, Stool, CSF, Sputum, Semen, Skin Scrapings, HVS).
- Support for on-the-fly custom specimen additions (**Other** option).
- Auto-generated unique barcode numbers for lab tubes.

### 4. Lab Testing & Parameter-level Entry
- **Dynamic Multi-Parameter Results**: Instead of single-value text entries, complex tests (like LFT, KFT/RFT, CBC, Lipid Profile) render individual input fields for all parameters.
- **Clinical Flags**: Direct assignment of **High (H)**, **Low (L)**, and **Normal (N)** flags against templates.

### 5. Pathology Verification & PDF Clinical Reports
- Multi-stage approval (Technician draft entry ➡️ Pathologist review & approval).
- Letter-sized **PDF Clinical Reports** featuring clean, professional grids, patient demographics, and color-coded flags (Red for High, Blue for Low).

### 6. Doctor & Patient Portals
- **Doctor Portal**: Physicians can order requisitions remotely and monitor their patients' results status.
- **Patient Portal**: Patients can view their profiles, billing invoices, and download released PDF results directly.

### 7. Quality Control (QC) & Non-Conformance Logs
- Control lot setup (Target values, standard deviation, expiry tracking).
- QCRun validation logs with automatic pass/fail alerts.
- Quality assurance logs for Non-Conformance events.

### 8. Supplier Inventory & Equipment Tracking
- Reagents stock monitoring, minimal stock alerts, and usage tracking.
- Analyzers calibration schedules and dynamic maintenance log tracking.

---

## 🛠️ Technology Stack
- **Backend Framework**: Django 5.x (Python)
- **Database**: MySQL 8.0
- **Frontend Layer**: Alpine.js, Tailwind CSS, Vanilla JS
- **PDF Generation**: ReportLab
- **Data Import**: openpyxl

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- Python 3.10+
- MySQL Server 8.0+

### 2. Setup Virtual Environment & Dependencies
```bash
# Clone the repository
git clone https://github.com/Mark-Finley/LMS-VT.git
cd LMS

# Initialize and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Configurations
Create a `.env` file in the root directory:
```env
DB_NAME=laboratory_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=your-django-secret-key
```

Run database migrations:
```bash
python manage.py migrate
```

### 4. Seed Database Catalogue & Demo Accounts
Run the customized seeding pipeline to populate roles, supplier details, and all **44 diagnostic tests** along with their clinical reference parameters from the template:
```bash
python manage.py seed_data
```

### 5. Run the Server
```bash
python manage.py runserver
```
Visit the application at `http://127.0.0.1:8000/`.

---

## 🔑 Demo Accounts

All demo accounts use the default password: **`Password123!`**

| Username | Role | Purpose |
| :--- | :--- | :--- |
| **`admin`** | Administrator | Full administrative controls and Test Catalogue config. |
| **`doctor`** | Doctor | Test Ordering and patient tracking dashboard. |
| **`patient`** | Patient | Profile lookup, invoice balance check, and report download. |
| **`technician`** | Lab Technician | Phlebotomy collections, results recording, and inventory. |
