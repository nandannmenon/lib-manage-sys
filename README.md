# Library Management System 

A full-featured web-based Library Management System built using Django and Django REST Framework. This system allows libraries to manage books, members, transactions, and administrative operations in a streamlined and efficient manner.

---

## Overview

This application provides an intuitive interface for students, librarians, and administrators to interact with the library system. Key functions include cataloging books, issuing and returning books, managing member records, handling overdue fines, and accessing digital resources.

---

## Key Features

### Book Management
- Add, update, and delete books
- Track book availability and copies
- Manage book metadata (title, author, publisher, genre)

### Member Management
- User registration and profile management
- Different membership levels (Standard, Premium)
- Borrowing history and contact details

### Borrowing & Returns
- Issue and return books
- Automatic due date and fine calculation
- Real-time availability tracking

### Financial Management
- Fine tracking and payment
- Membership fee handling
- Multiple payment methods supported

### Admin & Staff Management
- Secure login for library staff
- Manage user accounts and access levels
- Monitor overdue and returned books

---

## Technology Stack

- **Backend**: Django 4.2+
- **API Layer**: Django REST Framework 3.14+
- **Database**: SQLite (for development), MySQL (for production)
- **Authentication**: Django built-in auth

---

## Database Schema

Entities included:
- Books
- Authors
- Publishers
- Genres
- Members
- Employees
- Membership Plans
- Issues & Returns
- Fines

---
## Login Credentials

### **Student Login**
- **Username**: First name (from `data/member.csv`)
- **Password**: Member_ID
- Example: Username: nandan, Password: 521

### **Admin Login**
- **Username**: `admin`
- **Password**: `admin123`

---

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd lms_final
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create an admin user:
```bash
python manage.py createsuperuser
```

6. Run the server:
```bash
python manage.py runserver
```

---

## Project Structure

```
lms_final/
├── lms_portal/        # Project config and settings
│   ├── lms_app/       # Core application
│   └── manage.py
├── data/              # Fixtures or initial data
├── requirements.txt   # Dependency list
└── db-design.sql      # SQL schema
```

---

## REST API Overview

The system exposes API endpoints for:
- Book and member management
- Issue/return workflows
- Fine calculation and payments
- Search and filter functionality

---

**Note:** This is an academic project intended for learning purposes and small-scale deployment.
