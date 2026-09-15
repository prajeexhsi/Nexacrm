# NexaCRM

**Connect • Manage • Grow**

NexaCRM is a Django CRM workspace designed around the NexaCRM onboarding model: landing page → business selection → module selection → AI-style setup suggestion → ready workspace.

## Included modules
- Landing page and pricing
- Username/email login and account registration
- Business onboarding and workspace customization
- Dashboard with pipeline, follow-ups, tasks, students, courses and revenue KPIs
- Leads and converted customers
- Students
- Courses and batches
- Follow-ups
- Payments
- Tasks
- Marketing campaigns
- Support tickets
- WhatsApp message logging
- Reports and analytics
- Role dashboard
- User management
- Dark mode
- CSV lead export
- Responsive mobile layout
- WhiteNoise static files
- PostgreSQL-ready environment configuration
- Vercel Python entrypoint

## Local run
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Vercel
Use the Django preset, root directory `.`, and environment variables:
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=.vercel.app`
- `CSRF_TRUSTED_ORIGINS=https://*.vercel.app`
- `DB_ENGINE=sqlite` for demo/testing only

For persistent production CRM data, configure PostgreSQL.
