# Embassy Management ERPNext

[Powered by Viewertech](https://viewertech.net)

Embassy Management ERPNext is a reusable ERPNext v16 and Frappe v16 application for embassies, high commissions, consulates, permanent missions, and honorary consulates. It provides a configurable extension layer for consular services, online applications, appointments, document review, fees, officer workflow, dashboards, public portal UX, and multilingual embassy content.

The project uses public embassy application and appointment patterns as reference patterns only. No country, city, embassy, consular policy, fee rule, language, flag, emblem, or office location is hardcoded.

## Architecture

ERPNext and Frappe remain the system of record for standard records:

- Customer, Contact, Address, User, Website User
- File, Communication, Email Template, Notification
- Company, Item, Sales Invoice, Payment Entry, Payment Request, Mode of Payment
- Role, Workflow, Workflow State, Workflow Action
- Letter Head, Web Form, ToDo, Dashboard Chart, Number Card

The custom app `embassy_management` adds only embassy-specific DocTypes, portal controllers, rule evaluation, permissions, and consular workflow helpers. It does not modify ERPNext or Frappe core.

## Repository Layout

- `/apps/embassy_management` - reusable Frappe custom app
- `/docker` - Docker build notes and custom image Dockerfile
- `/scripts` - Ubuntu/Docker deployment and maintenance scripts
- `/docs` - deployment, handover, audit, security, and configuration guides
- `/import_templates` - CSV import templates for configuration data
- `/sample_data` - generic, non-official demo records
- `/nginx` - sample reverse proxy configuration
- `/backups` - backup target directory placeholder

## Quick Start on Ubuntu 24.04 LTS

1. Install prerequisites:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates
./scripts/install.sh
```

2. Configure environment:

```bash
cp .env.example .env
nano .env
```

3. Build and start containers:

```bash
docker compose build
docker compose up -d
```

4. Create the ERPNext site and install apps:

```bash
./scripts/create-site.sh
./scripts/install-apps.sh
```

5. Import generic presentation data when needed:

```bash
./scripts/load-sample-data.sh
```

The loader creates removable `EMSDEMO` records across the Embassy Management app and standard ERPNext masters: customers, contacts, addresses, suppliers, items, leads, projects, tasks, applicants, applications, appointments, document reviews, payment reviews, communications, and ToDos. Remove it after a presentation with:

```bash
./scripts/clear-sample-data.sh
```

6. Repair asset links if the frontend serves stale assets after rebuilds:

```bash
./scripts/repair-assets.sh
```

7. Open the site:

```text
http://localhost:8091
```

## Site Creation

The default scripts read `.env` values:

- `SITE_NAME`
- `ADMIN_PASSWORD`
- `DB_ROOT_PASSWORD`
- `DB_ROOT_USER`
- `DB_HOST`
- `DB_PORT`
- `SOCKETIO_PORT`
- `INSTALL_APPS`
- `HTTP_PUBLISH_PORT`
- `BACKUP_DIR`
- `BACKUP_RETENTION_DAYS`
- `DEFAULT_CURRENCY`
- `DEFAULT_COUNTRY`
- `DEFAULT_TIMEZONE`

Values with spaces can be quoted in `.env`, for example `DEFAULT_COUNTRY="United States"`. The scripts use a safe dotenv loader and do not execute `.env` as Bash.

The create-site script calls Frappe bench inside the Docker backend container and installs ERPNext first, then `embassy_management`.

## App Installation

The app can be installed on an existing ERPNext v16 site:

```bash
bench --site your-site.local install-app embassy_management
bench --site your-site.local migrate
bench --site your-site.local clear-cache
```

## Initial Configuration

Open Desk and configure:

1. **Embassy Settings** - mission name, type, countries, city, languages, branding, appointment windows, notices, letterhead, and contact channels.
2. **Consular Service** - enable services such as visa, passport, consular card, attestation, legalisation, civil registry, emergency travel document, or any local service.
3. **Application Form Template** - create sections and fields for each service.
4. **Application Form Rule** - configure eligibility, notices, document requirements, appointment requirements, and fee logic.
5. **Application Document Requirement** - define required documents per service and application.
6. **Consular Fee Rule** - link services to ERPNext Items and currency-specific fee rules.
7. **Appointment Slot** - define capacity, working days, public-holiday exclusions, locations, and officer assignments.
8. **Email Template** - edit multilingual templates for applicant and officer notifications.
9. **Workflow** - adjust state transitions per service where required.

## Branding

Branding is managed in **Embassy Settings**:

- Mission logo
- Emblem placeholder
- Letter Head
- Email footer
- Primary and secondary colours
- Portal URLs
- Public notices, privacy notice, declaration text, and confirmation text

No official flags, coats of arms, or government emblems are included. Replace placeholders only with client-supplied assets.

## Applicant Portal

The public portal is available under:

- `/embassy` - public landing/dashboard entry
- `/embassy/requirements` - configurable requirements checker
- `/embassy/apply` - application flow
- `/embassy/dashboard` - applicant dashboard

Applicant features:

- Register and sign in with Frappe website users
- Start, save, resume, and submit applications
- Track statuses
- Upload documents linked to Frappe File
- Book appointments where required
- View payment state and receipts
- Read applicant-facing communications
- Download summaries and approved outputs where configured

## Officer Review

Officers use the Embassy Management workspace:

- Case queue filters by service, status, priority, appointment date, and assigned officer
- Document review statuses: Accepted, Rejected, Unclear, Expired, Missing
- Additional document requests through Communication and Email Template
- Approval, rejection, escalation, reassignment, and decision-letter generation
- Finance review through Sales Invoice, Payment Entry, Payment Request, and Consular Payment Review

## Reports and Dashboards

Included reports:

- Applications by service, status, nationality, submission channel, and decision
- Pending officer review, documents, and payments
- Appointments by day and no-show appointments
- Revenue by service and month
- Processing time by service
- Rejection reasons
- Officer workload
- Document rejection summary

Dashboard number cards cover today, this week, this month, urgent cases, overdue cases, and processing-time indicators.

## Backups, Restore, and Update

```bash
./scripts/backup-site.sh
./scripts/restore-site.sh --database ./backups/site-backup.sql.gz
./scripts/update-site.sh
./scripts/clear-sample-data.sh
```

See [docs/ubuntu-full-setup-guide.md](docs/ubuntu-full-setup-guide.md), [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md), [docs/HANDOVER.md](docs/HANDOVER.md), and [docs/SECURITY.md](docs/SECURITY.md) for operating details.

## GitHub

Target repository:

```text
https://github.com/viewertech/Embassy_Management_ERPNext
```

## License

MIT. See [LICENSE](LICENSE).
