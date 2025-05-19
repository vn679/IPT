# Room Reservation System

A Django-based room reservation system with an intuitive dashboard and booking management features.

## Setup Instructions

1. Clone this repository to your local machine
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source .venv/bin/activate
     ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Apply database migrations:
   ```
   python manage.py migrate
   ```
6. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```
8. Visit http://127.0.0.1:8000 in your browser

## Project Structure

```
IPTfinal/
├── IPTfinal/              # Main Django project directory
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── .venv/                 # Virtual environment
├── db.sqlite3            # Database file
├── manage.py            # Django management script
├── README.md           # This file
└── requirements.txt    # Project dependencies
```

## Features

- Dashboard with real-time statistics
- Room reservation management
- Course-wise reservation tracking
- Weekly statistics visualization
- User-friendly interface
- Admin panel for system management 