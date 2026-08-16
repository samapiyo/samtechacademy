# SAMTECHACADEMY — Python/Flask Website

A starter online business platform built with Python, Flask and SQLite.

## Included
- Home page
- About page
- Services page
- Opportunities listing
- User registration and login
- Admin dashboard
- Add/delete opportunities
- Contact form with database storage
- Responsive design
- Prepared `.env` configuration for M-Pesa Daraja integration

## Run on Windows PowerShell

```powershell
cd samtechacademy_python
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Then open:
http://127.0.0.1:5000

## Create an admin account

After activating the virtual environment:

```powershell
flask --app app create-admin
```

The default admin password comes from `.env`. Change it before using the site publicly.

## Important
The M-Pesa section is configuration-ready, but live STK Push should be connected to Safaricom Daraja credentials and a publicly reachable callback endpoint before accepting real payments.

For production, move from SQLite to PostgreSQL/MySQL and turn off Flask debug mode.
