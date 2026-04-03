# Finance Data Processing & Access Control Backend

## Live API

https://backend-finance-dashboard.onrender.com/docs

---

## Overview

This project is a backend system for managing financial records with role-based access control.
Users interact with data at user, department, and organization levels depending on their role.

---

## Roles

**Admin**

* Manage users (create, update, activate/deactivate)
* Assign roles and departments
* Approve or reject records
* Access all records and analytics

**Analyst**

* View department-level data
* Access department analytics

**Viewer**

* View personal data
* View summary data

---

## Features

* JWT Authentication
* Role-Based Access Control (RBAC)
* Financial record management
* Dashboard analytics (aggregations)
* Department-level filtering using joins
* Approval workflow (pending, approved, rejected)
* Category handling (predefined and custom)
* Auto-generated employee ID

---

## Database Design

Tables:

* roles
* departments
* categories

* users:
- id
- name
- email
- role_id
- department_id
- is_active (true / false)

* records:
- id
- amount
- description
- type (income/expense)
- created_by
- status (pending/approved/rejected)

**Design Note**

* `records` does not store `department_id`
* Department is derived using:

  ```
  Record → User → Department
  ```
* Ensures normalization and avoids redundancy

---

## Authentication


* Click Authorize use USERNAME and PASSWORD from the demo credentials
* Leave remaining feilds empty 
* Click Authorize

---

## Demo Credentials

Admin
email: admin@test.com
password: 123456

Analyst
email: analyst@test.com
password: 123456

Viewer
email: user@test.com
password: 123456

---

## Dashboard APIs

### GET /dashboard/total-expense

* User → own expenses
* Analyst → own + department
* Admin → own + global

### GET /dashboard/total

* Returns income, expense, and net balance
* net_balance = income - expense

### GET /dashboard/category-wise

* Category-wise totals based on role

### GET /dashboard/monthly

* Month-wise totals (used for trend analysis)
* Helps visualize income/expense trends over time
* Months with no data are not included

### GET /dashboard/recent

* Last 5 records
* Analyst/Admin also see department/global records

### GET /dashboard/summary

* Status-based aggregation:

  * approved
  * pending
  * rejected
* Viewer → user only
* Analyst → user + department
* Admin → user + global

---

## Records APIs

### POST /records/

* Admin only
* Create financial record

### GET /records/my

* All users
* Returns own records

### GET /records/department

* Analyst, Admin
* Department records

### GET /records/all

* Admin only

### DELETE /records/{id}

* Admin only

### PATCH /records/{id}/status

* Admin only
* Approve or reject

### PUT /records/{id}

* Admin only
* Update record

### GET /records/filter

* Filter by type, category, dates

---

## Users APIs

### POST /users/

* Admin only

### GET /users/get-all

* Admin → all users
* Analyst → department users

### GET /users/get-categories

* Available to all roles

### PATCH /users/{id}

* Admin only

### GET /users/me

* Current user details

---

## Key Concepts

**Net Balance**

```
net_balance = income - expense
```

**Record Status**

* pending → waiting for approval
* approved → used in analytics
* rejected → ignored

---

## Tech Stack

* Backend: FastAPI
* Database: PostgreSQL
* ORM: SQLAlchemy
* Authentication: JWT
* Deployment: [Render](https://backend-finance-dashboard.onrender.com/docs)

---

## Setup

```
git clone https://github.com/sudharsan-051006/Backend-finance-dashboard
cd Backend-finance-dashboard

pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Design Decisions

* RBAC enforced at backend
* Department derived using joins
* Aggregations using SQL functions
* Status-based filtering for analytics
* Owner-based access for data integrity

---


## Author

S Sudharsan Reddy
Reference ID: TECV32KY