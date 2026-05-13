# HumanBackend - Authentication System

This project provides a robust authentication system built with Django and Django REST Framework, supporting standard Email/Password authentication and Google OAuth.

## Features

- **Custom User Model**: Uses `email` as the primary identifier instead of `username`.
- **JWT Authentication**: Secure stateless authentication using `djangorestframework-simplejwt`.
- **Email Registration**: Endpoint for creating new accounts with password confirmation.
- **Email Login**: Authenticate with email and password to receive JWT tokens.
- **Google Login**: Social authentication integration via `dj-rest-auth` and `django-allauth`.
- **CORS Support**: Configured to work seamlessly with frontend applications.

## Technology Stack

- **Backend**: Django 5.2.14
- **API Framework**: Django REST Framework
- **Authentication**: JWT (SimpleJWT), Social Auth (Allauth)
- **Database**: SQLite (default, can be swapped for PostgreSQL)

## Setup and Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd HumanBackend
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (for admin access)
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

## Configuration for Google Login

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and set up OAuth 2.0 credentials.
3. Add `http://localhost:8000/accounts/google/login/callback/` to your Authorized redirect URIs.
4. Log in to the Django Admin (`/admin/`).
5. Under **Sites**, ensure the domain matches your environment (e.g., `127.0.0.1:8000`).
6. Under **Social Accounts > Social Applications**, add a new application for Google:
   - **Provider**: Google
   - **Client id**: Your Google Client ID
   - **Secret key**: Your Google Client Secret
   - **Sites**: Move your site to the chosen sites list.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register a new user |
| `/api/auth/login/` | POST | Login with email/password |
| `/api/auth/google/` | POST | Social login with Google token |
| `/api/auth/token/refresh/` | POST | Refresh JWT access token |

### Registration Payload
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "yourpassword",
  "confirm_password": "yourpassword"
}
```

### Login Payload
```json
{
  "email": "john@example.com",
  "password": "yourpassword"
}
```

### Google Login Payload
```json
{
  "access_token": "GOOGLE_ACCESS_TOKEN"
}
```

## License

MIT License
