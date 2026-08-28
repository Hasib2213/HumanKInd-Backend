# 🌟 HumanKind Backend Service

[![Django](https://img.shields.io/badge/Django-5.2.14-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/django--rest--framework-3.15-red?style=for-the-badge)](https://www.django-rest-framework.org/)
[![JWT](https://img.shields.io/badge/Authentication-JWT--SimpleJWT-orange?style=for-the-badge)](https://django-rest-framework-simplejwt.readthedocs.io/)
[![Status](https://img.shields.io/badge/API_Status-Fully_Operational-brightgreen?style=for-the-badge)](file:///d:/Django_Personal_project/HumanKind_Backend/HumanBackend/README.md)

Welcome to the backend architecture powering the **HumanKind** ecosystem. This repository provides a highly scalable and secure Django REST Framework service that supports modern authentication flows, granular user profile management, customizable personalization options, rich community interactions, and subscription/plan controls.

---

## 🚀 Key Modules & Capabilities

- **🔐 Robust Auth Engine**: Standard Email/Password signup, Google Social OAuth 2.0 integration, and standard stateless JWT (JSON Web Token) rotations.
- **🛡️ Custom Admin & Portal Auth**: Specialized endpoints for Staff/Admin authentication complete with a robust 6-digit OTP password recovery flow.
- **👤 Profile Management & Saves**: Granular control of user attributes, location, contact, and profile avatar uploads. Features categorized user bookmark tables (Saved Posts, Saved Affirmations, Saved Meditations).
- **🎯 Personalization Engine**: Stores user preferences regarding daily mindfulness practices (interests, daily target duration, obstacle identification, mindfulness experience) to dynamically curate customized feeds.
- **🌤️ Daily Affirmation Service**: Proxies the FastAPI affirmation endpoint and caches one affirmation per calendar day so the same message stays visible until the next day.
- **🧘 AI Meditation Service**: Proxies the FastAPI meditation endpoint on each request, generating two guided meditations by mood without caching.
- **💬 Active Community Hub**: Full-featured posting center allowing optional audio attachments, complete anonymity options, nested commenting, post liking, post sharing increments, and a dedicated community reporting system for moderation.
- **💳 Premium Subscriptions**: Multi-tiered subscription plan configuration, supporting 7-day trials, activation cycles, and automatic expiration checks.

---

## 🛠️ Technology Stack

- **Framework**: Django `v5.2.14`
- **API Framework**: Django REST Framework `v3.15`
- **Security**: SimpleJWT (JSON Web Token), Django-Allauth, DJ-Rest-Auth
- **Database**: MongoDB Atlas via Django MongoDB Backend (or SQLite if `DATABASE_ENGINE=sqlite3`)
- **File Uploads**: Supports local or cloud storage for profile pictures and high-quality community audio uploads.

---

## 💻 Quick Start & Setup

### 1. Environment Preparation
```bash
# Clone the repository
git clone <repository-url>
cd HumanBackend

# Set up virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Firebase Setup (For Push Notifications)
To enable push notifications in the app, you must link your Firebase project:
1. Go to your **Firebase Console** -> Project Settings -> Service Accounts.
2. Click **Generate New Private Key**.
3. Download the `.json` file.
4. Rename the downloaded file to exactly **`firebase-adminsdk.json`**.
5. Place this file inside the main project directory (the same folder where `manage.py` is located).

### 4. Database Initial Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

If you are using MongoDB Atlas, add these variables to your `.env` file:

```env
DATABASE_ENGINE=django_mongodb_backend
MONGO_URI=mongodb+srv://<username>:<password>@nikooai.lri8ass.mongodb.net/?appName=NIkooAI
MONGO_DB_NAME=HumanKind
```

Keep the database name separate because the Atlas URI you shared does not include one.

### 4. Run Development Server
```bash
python manage.py runserver
```

---

## ⚙️ Google Social OAuth 2.0 Integration Setup

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create/select a project, navigate to **Credentials**, and configure **OAuth 2.0 Credentials**.
3. Register the Authorized redirect URIs: `http://localhost:8000/accounts/google/login/callback/`.
4. Log into the Django admin dashboard (`/admin/`).
5. Under **Sites**, ensure the default site matches your environment's active domain (e.g. `127.0.0.1:8000`).
6. Navigate to **Social Accounts > Social Applications** and insert a new application configuration:
   - **Provider**: Google
   - **Client id**: *Your Google Client ID*
   - **Secret key**: *Your Google Client Secret*
   - **Sites**: Move your configured Site to the **Chosen Sites** list.

## 💳 SSLCommerz Sandbox Setup

Add these variables to your `.env` file before using subscription checkout:

```env
STORE_ID=cleve6084e47685c74
STORE_PASS=cleve6084e47685c74@ssl
SSL_COMMERZ_SANDBOX=True
```

The subscription payment initiation endpoint is now:

- `POST /api/subscriptions/sslcommerz/subscribe/`

The gateway callback endpoints are:

- `GET|POST /api/subscriptions/sslcommerz/success/`
- `GET|POST /api/subscriptions/sslcommerz/fail/`
- `GET|POST /api/subscriptions/sslcommerz/cancel/`

---

## 📋 Comprehensive API Endpoint Checklist

Here is the master checklist detailing every endpoint developed in this backend system. You can mark items off as you perform integration testing.

### 🔑 1. Authentication & Admin Portal (`Authapp`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :---: | :--- | :---: | :--- |
| **`[x]`** | `POST` | `/api/auth/register/` | Public | Standard email registration for new user accounts. |
| **`[x]`** | `POST` | `/api/auth/login/` | Public | Standard email/password login to obtain access/refresh JWT tokens. |
| **`[x]`** | `POST` | `/api/auth/google/` | Public | Authenticate a user utilizing a Google OAuth2 access token. |
| **`[x]`** | `POST` | `/api/auth/token/refresh/` | Public | Refresh the temporary JWT access token. |
| **`[x]`** | `POST` | `/api/auth/admin/login/` | Staff User | Administrative / Staff portal login to receive administrative credentials. |
| **`[x]`** | `POST` | `/api/auth/admin/forgot-password/` | Staff User | Trigger an email-based password recovery OTP code (6-digits). |
| **`[x]`** | `POST` | `/api/auth/admin/verify-otp/` | Staff User | Verify an OTP code received by administrative staff. |
| **`[x]`** | `POST` | `/api/auth/admin/reset-password/` | Staff User | Overwrite an administrative password using a verified OTP token. |

### 👤 2. User Profile Management (`user_profile`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :---: | :--- | :---: | :--- |
| **`[x]`** | `GET` | `/api/profile/me/` | JWT (Required) | Retrieve the authenticated user's current profile card. |
| **`[x]`** | `PUT` / `PATCH` | `/api/profile/me/` | JWT (Required) | Update user profile data (full name, phone, location, avatar). |
| **`[x]`** | `GET` | `/api/profile/saved/posts/` | JWT (Required) | Fetch the user's bookmarked / saved community posts. |
| **`[x]`** | `GET` | `/api/profile/saved/affirmations/` | JWT (Required) | Fetch the user's bookmarked / saved daily affirmations. |
| **`[x]`** | `GET` | `/api/profile/saved/meditations/` | JWT (Required) | Fetch the user's bookmarked / saved meditation audio courses. |
| **`[x]`** | `DELETE` | `/api/profile/delete-account/` | JWT (Required) | Cascade-delete user account (removes profile, posts, preferences, etc.). |
| **`[x]`** | `POST` | `/api/profile/logout/` | JWT (Required) | Perform logout by blacklisting the associated Refresh Token. |

### 🎯 3. Personalization Engine (`UserPersonalization`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :---: | :--- | :---: | :--- |
| **`[x]`** | `GET` | `/api/personalization/preferences/` | JWT (Required) | Get current user's mindfulness/habit preferences. Creates default if none exists. |
| **`[x]`** | `PUT` / `PATCH` | `/api/personalization/preferences/` | JWT (Required) | Modify and update customized onboarding preferences/topics. |

### 🌤️ 4. Daily Affirmations (`content`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :--- | :--- | :---: | :--- |
| **`[x]`** | `GET` / `POST` | `/api/content/daily-affirmation/` | Public | Fetch the current day's affirmation from the FastAPI service and reuse the cached result until the date changes. |

### 🧘 5. AI Meditations (`content`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :--- | :--- | :---: | :--- |
| **`[x]`** | `POST` | `/api/content/ai-meditation/` | Public | Generate a two-part meditation by mood on demand. (Automatically saves `mood` if passed). |
| **`[x]`** | `GET` | `/api/content/ai-meditation/?user_id=<id>&content_id=<id>` | Public | Retrieve a previously generated meditation from the FastAPI service. |

### 📔 6. Journal (`content`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :--- | :--- | :---: | :--- |
| **`[x]`** | `POST` | `/api/content/journal/` | Public | Refine a journal question and prompt through the FastAPI service on demand. |

### 💬 7. Community Hub (`community`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :---: | :--- | :---: | :--- |
| **`[x]`** | `GET` | `/api/community/posts/` | JWT (Required) | Retrieve the community feed. |
| **`[x]`** | `POST` | `/api/community/posts/` | JWT (Required) | Share a post (supports text, multiple `images`, multiple `videos`, audio uploads, and optional anonymity). |
| **`[x]`** | `GET` | `/api/community/posts/<str:pk>/` | JWT (Required) | Retrieve details for a single community post. |
| **`[x]`** | `PUT` / `PATCH` | `/api/community/posts/<str:pk>/` | JWT (Required) | Modify contents of a post (restricted to post author). |
| **`[x]`** | `DELETE` | `/api/community/posts/<str:pk>/` | JWT (Required) | Permanently delete a community post (restricted to post author). |
| **`[x]`** | `GET` | `/api/community/posts/<str:post_id>/comments/` | JWT (Required) | Fetch comments associated with a specific community post. |
| **`[x]`** | `POST` | `/api/community/posts/<str:post_id>/comments/` | JWT (Required) | Write a new comment on a community post. |
| **`[x]`** | `POST` | `/api/community/posts/<str:post_id>/like/` | JWT (Required) | Toggle like state (increments or decrements total likes). |
| **`[x]`** | `POST` | `/api/community/posts/<str:post_id>/save/` | JWT (Required) | Toggle save/bookmark state. |
| **`[x]`** | `POST` | `/api/community/posts/<str:post_id>/share/` | JWT (Required) | Increment post share count tracking. |
| **`[x]`** | `POST` | `/api/community/reports/` | JWT (Required) | File an anonymous or registered report against a post for moderation. |

### 💳 8. Subscription Services (`subscriptions`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :---: | :--- | :---: | :--- |
| **`[x]`** | `GET` | `/api/subscriptions/plans/` | JWT (Required) | View list of active premium tier configurations (price, duration). |
| **`[x]`** | `GET` | `/api/subscriptions/my-subscription/` | JWT (Required) | Check current user's active billing tier, trial state, and date range. |
| **`[x]`** | `POST` | `/api/subscriptions/subscribe/` | JWT (Required) | Subscribe to a specific plan (automatically calculates trials). |
| **`[x]`** | `POST` | `/api/subscriptions/cancel/` | JWT (Required) | Cancel the active subscription renewal sequence. |

### 🔔 9. In-App Notifications (`notifications`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :---: | :--- | :---: | :--- |
| **`[x]`** | `GET` | `/api/notifications/` | JWT (Required) | Retrieve the user's notification alerts list. |
| **`[x]`** | `POST` | `/api/notifications/read/` | JWT (Required) | Mark all user's notifications as read. |
| **`[x]`** | `PATCH` | `/api/notifications/read/` | JWT (Required) | Mark a specific notification ID as read. |

### 📈 10. Progress Dashboard (`progress`)
| Status | Method | Endpoint | Authentication | Function / Action |
| :---: | :---: | :--- | :---: | :--- |
| **`[x]`** | `GET` | `/api/progress/` | JWT (Required) | Retrieve the full progress dashboard data (streaks, weekly activity, community voice, and 7-day mood chart). |
| **`[x]`** | `POST` | `/api/progress/mood/` | JWT (Required) | Manually log a user's daily mood ("Happy", "Confident", etc.). |
| **`[x]`** | `POST` | `/api/progress/activity/` | JWT (Required) | Log a completed activity ("calming_session", "mindful_breathing", "affirmation"). |

---

## 📦 Request / Response Payload Reference Guide

> [!TIP]
> Click on the sections below to expand and view exact request payloads, response templates, and field choices.

<details>
<summary><b>🔐 Authentication Endpoints</b></summary>

#### User Registration (`POST /api/auth/register/`)
* **Payload Structure**:
  ```json
  {
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }
  ```

#### User Login (`POST /api/auth/login/`)
* **Payload Structure**:
  ```json
  {
    "email": "jane.smith@example.com",
    "password": "SecurePassword123!"
  }
  ```
* **Success Response (200 OK)**:
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "email": "jane.smith@example.com",
      "first_name": "Jane",
      "last_name": "Smith"
    }
  }
  ```

#### Google OAuth2 Authentication (`POST /api/auth/google/`)
* **Payload Structure**:
  ```json
  {
    "access_token": "ya29.a0AfH6SM..."
  }
  ```
</details>

<details>
<summary><b>🛡️ Staff & Admin Recovery Endpoints</b></summary>

#### Admin Forgot Password (`POST /api/auth/admin/forgot-password/`)
* **Payload Structure**:
  ```json
  {
    "email": "admin@humankind.com"
  }
  ```

#### Admin Verify OTP (`POST /api/auth/admin/verify-otp/`)
* **Payload Structure**:
  ```json
  {
    "email": "admin@humankind.com",
    "otp_code": "489210"
  }
  ```

#### Admin Reset Password (`POST /api/auth/admin/reset-password/`)
* **Payload Structure**:
  ```json
  {
    "email": "admin@humankind.com",
    "otp_code": "489210",
    "new_password": "SuperNewPassword2026!",
    "confirm_password": "SuperNewPassword2026!"
  }
  ```
</details>

<details>
<summary><b>🎯 Personalization Engine Settings</b></summary>

#### Retrieve/Update Preferences (`GET | PUT | PATCH /api/personalization/preferences/`)
* **Payload Structure**:
  ```json
  {
    "topics": ["reduce_stress", "better_sleep", "gratitude"],
    "tone": "gentle",
    "birth_year": 1995,
    "obstacles": ["limited_time", "procrastination"],
    "practice_time": "10min",
    "experience": "beginner"
  }
  ```

* **Valid Payload Fields & Constraints**:
  - **`topics`** (List of strings selected from):
    - `reduce_stress` (Reduce Stress)
    - `better_sleep` (Better Sleep)
    - `focus` (Focus)
    - `anxiety_relief` (Anxiety Relief)
    - `self_love` (Self-love)
    - `confidence` (Confidence)
    - `motivation` (Motivation)
    - `trauma_depression` (Get over trauma and depression)
    - `gratitude` (Develop Gratitude)
    - `reduce_anxiety` (Reduce Anxiety)
    - `self_esteem` (Build Self Esteem)
    - `increase_happiness` (Increase Happiness)
    - `improve_performance` (Improve Performance)
  - **`tone`** (String): `gentle`, `bold`, `spiritual`
  - **`birth_year`** (Integer): Must be between 1900 and current year.
  - **`obstacles`** (List of strings selected from):
    - `low_motivation` (Low motivation)
    - `limited_time` (Limited time)
    - `unclear_goals` (Unclear goals)
    - `fear_failure` (Fear of failure)
    - `procrastination` (Procrastination)
    - `financial_constraints` (Financial constraints)
  - **`practice_time`** (String): `5min`, `10min`, `20min`
  - **`experience`** (String): `beginner`, `few_times`, `a_lot`
</details>

<details>
<summary><b>💬 Community Action JSON Examples</b></summary>

#### Create Post (`POST /api/community/posts/`)
* **Payload (Multipart Form-Data)**:
  - `content`: "Taking some deep breaths today helps centering my mind." (Text)
  - `audio_file`: [Optional Binary audio recording file]
  - `is_anonymous`: `true` or `false`
* **Response (201 Created)**:
  ```json
  {
    "id": 14,
    "user": null, // Returns null when is_anonymous is true
    "content": "Taking some deep breaths today helps centering my mind.",
    "audio_file": null,
    "is_anonymous": true,
    "share_count": 0,
    "likes_count": 0,
    "comments_count": 0,
    "is_liked": false,
    "is_saved": false,
    "created_at": "2026-05-22T19:24:00Z",
    "updated_at": "2026-05-22T19:24:00Z"
  }
  ```

#### Create Comment (`POST /api/community/posts/<post_id>/comments/`)
* **Payload Structure**:
  ```json
  {
    "content": "This is so relatable! Thank you for sharing."
  }
  ```


  To reply each other ,at same url give this input:
  {
  "content": "Eta reply",
  "parent": 12
}

#### Submit Content Report (`POST /api/community/reports/`)
* **Payload Structure**:
  ```json
  {
    "post": 14,
    "title": "Spam or Off-topic",
    "description": "This user is advertising external links on the page."
  }
  ```
</details>

<details>
<summary><b>💳 Subscription Flow JSON Examples</b></summary>

#### Subscribe to Plan (`POST /api/subscriptions/subscribe/`)
* **Payload Structure**:
  ```json
  {
    "plan_id": 2
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "id": 1,
    "plan": {
      "id": 2,
      "name": "MONTHLY ACCESS",
      "description": "Full access, billed monthly",
      "price": "50.00",
      "duration_days": 30,
      "most_popular": false,
      "trial_days": 3,
      "is_active": true
    },
    "status": "trialing",
    "trial_start_date": "2026-05-22T19:28:44Z",
    "trial_end_date": "2026-05-25T19:28:44Z",
    "current_period_start": null,
    "current_period_end": null,
    "is_canceled": false
  }
  ```
</details>

<details>
<summary><b>🔔 In-App Notification Flow Examples</b></summary>

#### Fetch User Notifications (`GET /api/notifications/`)
* **Supported `notification_type` values**:
  - `subscription`: Trial expiration/billing alerts.
  - `like`: Someone liked your community post.
  - `comment`: Someone commented on your community post.
  - `share`: Someone shared your community post.
  - `info` / `alert`: General system info and alerts.

* **Response (200 OK)**:
  ```json
  [
    {
      "id": 1,
      "title": "Subscription Trial Ending Soon",
      "message": "Your trial for plan 'YEARLY ACCESS' will end in 2 days (on 2026-05-24). Subscribe to a premium tier to keep unlimited access.",
      "notification_type": "subscription",
      "is_read": false,
      "created_at": "2026-05-22T16:18:33.123456Z"
    }
  ]
  ```

#### Mark Specific Notification as Read (`PATCH /api/notifications/read/`)
* **Payload Structure**:
  ```json
  {
    "notification_id": 1
  }
  ```
* **Response (200 OK)**:
  ```json
  {
    "id": 1,
    "title": "Subscription Trial Ending Soon",
    "message": "Your trial for plan 'YEARLY ACCESS' will end in 2 days (on 2026-05-24). Subscribe to a premium tier to keep unlimited access.",
    "notification_type": "subscription",
    "is_read": true,
    "created_at": "2026-05-22T16:18:33.123456Z"
  }
  ```

#### Mark All Notifications as Read (`POST /api/notifications/read/`)
* **Response (200 OK)**:
  ```json
  {
    "message": "All notifications marked as read."
  }
  ```
</details>

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

