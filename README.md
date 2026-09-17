# Snip API
Django/DRF API for the Snip portfolio link analytics demo. Supabase is the sole identity provider; the API validates Supabase access tokens directly.

## Local development
1. Copy `.env.example` to `.env` and set the Supabase values.
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt && python manage.py migrate`
4. `python manage.py runserver`

## Production contract
Use managed PostgreSQL. Set `DEBUG=false`, a random `SECRET_KEY`, `DATABASE_URL`, canonical `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, and `SUPABASE_URL`. Run migrations as a release step. Health: `/healthz/`; database readiness: `/readyz/`; API docs: `/api/docs/`.

Never use SQLite on an ephemeral host. Free services may sleep, so this portfolio demo must show a clear warming-up state in the UI and should not claim an uptime SLA.
