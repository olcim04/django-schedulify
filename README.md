# Django Schedulify

Schedulify is a simple full-stack scheduling app built with Django (backend) and React (frontend). It allows users to manage tasks or events efficiently in a clean UI.

## 🛠 Features

- Django backend with REST API
- React frontend using functional components
- Basic scheduling/task management
- SQLite database for local development
- Environment variable support with `.env`

## 🧰 Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: React, Vite, JavaScript
- **Database**: SQLite (for development)
- **Deployment-ready** structure

## 🚀 Getting Started

### Backend (Django)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and start server
python manage.py migrate
python manage.py runserver
