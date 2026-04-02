# 💰 Finance Data Processing & Access Control Backend

## 🚀 Live API

👉 https://backend-finance-dashboard.onrender.com/docs

> Use this link to test all APIs directly via Swagger UI.

---

## 📌 Project Overview

This project is a backend system for managing financial records within a company.
It supports role-based access control, financial data tracking, and dashboard analytics.

The system is designed to simulate a real-world finance dashboard used by organizations.

---

## 👥 User Roles

### 🔴 Admin (HR)

* Create and manage users
* Assign roles and departments
* Approve or reject financial records
* View all records and analytics

### 🟡 Analyst

* View department-level financial data
* Analyze spending trends

### 🔵 User (Employee)

* Create expense records
* View own records

---

## 🧱 Features

* 🔐 Authentication using JWT
* 👥 Role-based access control (RBAC)
* 🧾 Financial record management (CRUD)
* 📊 Dashboard analytics
* 🏢 Department-based filtering
* ⏳ Approval workflow with deadline
* 🆔 Auto-generated Employee ID (Year-based)

---

## 🗄️ Database Design

Main tables:

* **users** → stores user details
* **roles** → admin, analyst, user
* **departments** → organizational units
* **records** → financial transactions
* **categories** → expense categories

---

## 🔐 Authentication

Login to get token:

```
POST /auth/login
```

Use token in Swagger:

👉 Click **Authorize** → paste token

---

## 📊 API Endpoints

### 👤 Users

* `GET /users/` → Get all users (Admin only)
* `PATCH /users/{id}` → Update role / department

### 🧾 Records

* `POST /records/` → Create record
* `GET /records/` → Get the all records
* `GET /records/my` → Get own records
* `GET /records/department` → Department records
* `PATCH /records/{id}/status` → Approve/Reject/Pending (Admin)

### 📊 Dashboard

* `GET /dashboard/total-expense`
* `GET /dashboard/category-wise`
* `GET /dashboard/monthly`
* `GET /dashboard/recent`

---

## 🧪 Demo Credentials

### 🔴 Admin

```
email: admin@test.com  
password: 123456
```

### 🟡 Analyst

```
email: analyst@test.com  
password: 123456
```

### 🔵 User

```
email: user@test.com  
password: 123456
```

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **Database:** PostgreSQL (Neon DB)
* **ORM:** SQLAlchemy
* **Auth:** JWT (python-jose)
* **Deployment:** Render

---

## 🛠️ Local Setup (Optional)

```bash
git clone <your-repo>
cd project

pip install -r requirements.txt
```

Create `.env`:

```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret
```

Run server:

```bash
uvicorn main:app --reload
```

---

## 🧠 Design Decisions

* Employee ID is immutable (not updated on role/department change)
* Role-based filtering enforced at backend
* Dashboard APIs use aggregation queries
* Approval workflow implemented using status + deadline

---

## 🚀 Future Improvements

* Pagination & filtering
* CSV export
* Notifications for approval deadlines
* Frontend dashboard integration

---

## 🏆 Conclusion

This project demonstrates backend design principles including:

* Clean architecture
* Data modeling
* Access control
* Aggregation logic
* Real-world workflow handling

---

## 👨‍💻 Author

Sudharsan Reddy
