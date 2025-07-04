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
```


### Frontend (React)

The frontend of this project is built using **React** with **Vite** for fast development. It is located in the `frontend/` directory.

#### To run the frontend:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```


### Project Structure

```bash
django-schedulify/
├── backend/                # Django backend app
│   ├──  manage.py
│   ├── api/
│   ├── mojprojekt/
│   └── db.sqlite3
├── frontend/               # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── .gitignore
└── README.md

```
