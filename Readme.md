# 🛒 Supermarket Management System

A terminal-based Python application designed to manage a virtual supermarket. It supports **admin** and **customer** roles with full functionality for product management, shopping, and order tracking, using **SQLite** for backend data storage.

---

## 🚀 Features

### 👥 User Roles
- **Admin**
  - Register with a secret key.
  - Add/view sections.
  - Add/view/update/remove products.
  - View order logs.
- **Customer**
  - Browse product sections.
  - Add products to cart.
  - Checkout with order confirmation.
  - View a detailed summary of purchases.

### 🛠️ System Components
- SQLite database with tables for:
  - Users
  - Sections
  - Products
  - Orders
- Session-based cart system for customers.
- Robust input handling and validation.
- Auto-close database on exit.

---

## 🗃️ Database Schema

### `users`
| id | username | password | role    |
|----|----------|----------|---------|
| PK | TEXT     | TEXT     | TEXT    |

### `sections`
| id | name     |
|----|----------|
| PK | TEXT     |

### `products`
| id | name | price | stock | section_id |
|----|------|-------|-------|------------|
| PK | TEXT | REAL  | INT   | FK         |

### `orders`
| id | username | product_name | quantity | total_price | timestamp |
|----|----------|--------------|----------|-------------|-----------|
| PK | TEXT     | TEXT         | INT      | REAL        | DATETIME  |

---

## 🧑‍💻 Getting Started

### Prerequisites
- Python 3.x
- SQLite3 (comes with Python)

### Run the Project
```bash
python system.py
🔑 Admin Registration Key
Default admin registration key: admin123
Make sure to change this in production:
Edit the ADMIN_KEY variable in system.py.



💡 Author
Made with ❤️ by [ aisha karam ,mariam marwan ,adham ]









