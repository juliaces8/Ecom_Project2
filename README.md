# MegaStore Multi-Vendor E-Commerce Platform

MegaStore is a Django-based marketplace where Vendors can manage digital storefronts and Buyers can purchase products and leave verified reviews.

---

## 🛠️ Novice Setup Guide
Follow these steps to get the project running on your local machine.

### 1. Prerequisites
Before starting, ensure you have the following installed:
* **Python 3.10 or higher**
* **XAMPP** (or MariaDB/MySQL server)
* **Code Editor** (like VS Code)

### 2. Prepare the Database
1. Open the **XAMPP Control Panel**.
2. Click **Start** next to the **MySQL** module.
3. Open your browser and go to `http://localhost/phpmyadmin/`.
4. Create a new database named `megastore_db` (or the name specified in your `settings.py`).

### 3. Environment Setup
Open your terminal in the project folder and run:
```powershell
# Create a virtual environment to keep dependencies organized
python -m venv .venv

# Activate the environment (Windows)
.\.venv\Scripts\Activate.ps1

# Install all required libraries (Django, Pillow, PyMySQL, etc.)
pip install -r requirements.txt

4. Apply Database Migrations

This sets up the tables for products, stores, and users:

python manage.py makemigrations
python manage.py migrate

5. Start the Application

python manage.py runserver

Now, open your browser and go to: http://127.0.0.1:8000/

🚀 Key Features
🛒 Buyer Capabilities
Product Discovery: Browse a full catalog of products with detailed descriptions and pricing.

Dynamic Cart Management: Add items to a session-based shopping cart. Buyers can manually type in quantities for bulk orders, providing a smoother UX than repetitive clicking.

Secure Checkout: A streamlined checkout process that generates an order history and sends an automated HTML invoice to the user's email.

Verified Reviews: Buyers can rate and review products. Reviews are automatically flagged with a "Verified Purchase" badge if the system confirms the buyer has previously ordered that item.

🏪 Vendor Capabilities
Store Management: Vendors can create and manage unique digital storefronts. A store description is mandatory to ensure professional-quality listings.

Inventory Control: Vendors have a dedicated dashboard to add, edit, or delete products.

Review Dashboard: A centralized "Customer Reviews" feed allows Vendors to monitor feedback across all their products in one place, without needing to browse individual product pages.

Social Integration: Automatic posting to X (Twitter) via API whenever a new store or product is created to drive external traffic.

🛠️ Technical Improvements & Data Integrity
Duplicate Email Prevention: The registration system validates email addresses to ensure every account is unique, preventing issues with password recovery and invoicing.

Stock Validation: The system performs a real-time inventory check during checkout. It prevents transactions that exceed available stock, eliminating the DataError: Out of range crash found in previous versions.

Role-Based Access Control: Strict separation of concerns ensures that Vendors cannot access or use the shopping cart, preserving the logic of a multi-vendor marketplace.

PEP 8 Compliance: All Python logic (models, views, and forms) is fully documented with docstrings for better maintainability and user documentation.