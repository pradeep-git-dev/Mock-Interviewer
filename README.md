# Mock Interviewer

A no-account mock interview app built with Django.

## What It Does
- Runs a 25-question interview session (`/api/start/`, `/api/answer/`).
- Uses browser-side voice features for question narration and voice input.
- Stores analytics/history in browser `localStorage` only.
- Provides a dedicated dashboard at `/past-scores/`.
- Has no login/signup requirement.

## Important Architecture Notes
- **No database is used** in runtime or deployment.
- Django sessions use signed cookies (`SESSION_ENGINE = django.contrib.sessions.backends.signed_cookies`).
- Legacy auth URLs are redirected to home for compatibility:
  - `/signin/`, `/signup/`, `/logout/`, `/signin/submit/`, `/signup/submit/` -> `/`

## Tech Stack
- Python 3.13
- Django 5.x
- Vercel Python runtime (`api/index.py`)

## Local Development
1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run server:

```bash
python manage.py runserver
```

4. Open:
- `http://127.0.0.1:8000/` (Interview page)
- `http://127.0.0.1:8000/past-scores/` (Dashboard page)

## Run Tests

```bash
python manage.py test
python manage.py check
```

## Deploy to Vercel
This repo is already configured with `vercel.json` to route all requests to `api/index.py`.

### Required Environment Variables
- `SECRET_KEY` = your production Django secret key
- `DEBUG` = `false`

Optional:
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

## Troubleshooting
### 404 on `/signin/`
If you still see `/signin/` 404 in production, your deployment is likely running an older build. Redeploy latest commit.

### Django debug page visible on Vercel
Ensure `DEBUG=false` in Vercel environment variables.

## Project Structure (key files)
- `mock/interviewer/views.py` - interview APIs and page views
- `mock/interviewer/urls.py` - routes including legacy redirect paths
- `mock/interviewer/templates/interviewer/index.html` - interview UI
- `mock/interviewer/templates/interviewer/past_scores.html` - dashboard UI
- `mock/mock/settings.py` - DB-free Django settings
- `mock/vercel.json` - Vercel routing config
- `mock/api/index.py` - Vercel entrypoint
