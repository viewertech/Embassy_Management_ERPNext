# Ubuntu Full Setup Guide

[Powered by Viewertech](https://viewertech.net)

This guide walks an embassy, high commission, consulate, permanent mission, or diplomatic mission IT administrator through deploying the full Embassy Management ERPNext stack on Ubuntu 24.04 LTS.

The stack uses:

- ERPNext v16
- Frappe v16
- Custom Frappe app: `embassy_management`
- Docker Compose
- MariaDB and Redis containers
- Optional host nginx reverse proxy

ERPNext and Frappe core are not modified. The custom app provides a reusable embassy-specific extension layer for consular services, applications, appointments, fees, document review, workflows, reports, and applicant portal UX.

## 1. Prepare the Server

Recommended minimum for a pilot:

- Ubuntu 24.04 LTS
- 4 CPU cores
- 8 GB RAM
- 100 GB disk
- Static IP address
- DNS name if using a production URL

Recommended for production:

- 8 CPU cores or more
- 16 GB RAM or more
- 250 GB disk or more
- Separate encrypted backup storage
- TLS certificate through mission nginx, institutional reverse proxy, or an approved load balancer

Create or use a non-root administrator account with `sudo` access.

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

After reboot, reconnect to the server.

## 2. Get the Repository onto Ubuntu

Choose one of these options.

If the server has GitHub access:

```bash
sudo apt update
sudo apt install -y git
sudo mkdir -p /opt
sudo chown "$USER:$USER" /opt
cd /opt
git clone https://github.com/viewertech/Embassy_Management_ERPNext.git embassy_management_erpnext
cd /opt/embassy_management_erpnext
```

If the GitHub repository is private or the server is not authenticated, copy the repository folder to the server using `scp`, SFTP, or an approved deployment process.

Example from a workstation:

```bash
scp -r Embassy_Management_ERPNext user@SERVER-IP:/opt/embassy_management_erpnext
```

Then on the server:

```bash
cd /opt/embassy_management_erpnext
```

## 3. Install Docker and Docker Compose

Make the scripts executable and run the installer:

```bash
chmod +x scripts/*.sh
sudo ./scripts/install.sh
```

The installer adds your user to the `docker` group. Apply the new group membership:

```bash
newgrp docker
```

Or log out and log back in.

Confirm Docker works:

```bash
docker --version
docker compose version
```

## 4. Choose the ERPNext Host Port

For this deployment guide, the system publishes ERPNext on host port `8091` because ports `8080` and `8090` are already in use on the target server.

Check whether port `8091` is available:

```bash
sudo ss -ltnp | grep ':8091 ' || true
```

If the command prints nothing, port `8091` is free.

If another service is also using `8091`, choose another free port such as `8092`, `8093`, or `18080`. Avoid `8080` and `8090` on this server because they are already allocated.

Important: only change the host port in `.env`. The container still listens on internal port `8080`.

## 5. Create the Environment File

Copy the example file:

```bash
cp .env.example .env
nano .env
```

Set strong values:

```text
SITE_NAME=embassy.example.org
FRAPPE_SITE_NAME_HEADER=embassy.example.org
ADMIN_PASSWORD=replace-with-strong-admin-password
DB_ROOT_PASSWORD=replace-with-strong-db-password
MYSQL_ROOT_PASSWORD=replace-with-the-same-db-password
MARIADB_ROOT_PASSWORD=replace-with-the-same-db-password
```

Keep the database settings unless your mission has an approved external database design:

```text
DB_ROOT_USER=root
DB_HOST=mariadb
DB_PORT=3306
SOCKETIO_PORT=9000
INSTALL_APPS=erpnext,embassy_management
```

Set defaults for the mission:

```text
DEFAULT_CURRENCY=USD
DEFAULT_COUNTRY=United States
DEFAULT_TIMEZONE=Etc/UTC
```

Use the free host port selected above:

```text
HTTP_PUBLISH_PORT=8091
```

If `8091` is already in use, set another free host port:

```text
HTTP_PUBLISH_PORT=8092
```

Set backup retention:

```text
BACKUP_DIR=./backups
BACKUP_RETENTION_DAYS=14
```

Save the file.

Generate strong passwords if needed:

```bash
openssl rand -base64 32
```

## 6. Open the Firewall Port

If using Ubuntu firewall and publishing directly on `8091`:

```bash
sudo ufw allow 8091/tcp
```

If using a different port, for example `8092`:

```bash
sudo ufw allow 8092/tcp
```

If using a production nginx reverse proxy with TLS, expose only HTTP/HTTPS as required by mission policy:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 7. Build and Create the ERPNext Site

Run:

```bash
./scripts/create-site.sh
```

This will:

1. Build the custom Docker image.
2. Start MariaDB, Redis, backend, frontend, workers, websocket, and scheduler.
3. Create the ERPNext site from `SITE_NAME` if it does not already exist.
4. Install `erpnext` and `embassy_management`.
5. Repair the Frappe Docker asset layout.
6. Run migrations and clear caches.

The first build can take several minutes.

## 8. Confirm Containers Are Running

```bash
docker compose ps
```

Expected services include:

- `mariadb`
- `redis-cache`
- `redis-queue`
- `backend`
- `frontend`
- `websocket`
- `queue-short`
- `queue-long`
- `scheduler`

Check logs if needed:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

## 9. Open ERPNext

If using the documented port:

```text
http://SERVER-IP:8091
```

If you changed the host port, for example to `8092`:

```text
http://SERVER-IP:8092
```

Log in with:

```text
Username: Administrator
Password: value of ADMIN_PASSWORD from .env
```

## 10. Change the ERPNext Host Port Later

If ERPNext is already running and you later discover the host port conflicts with another service:

1. Edit `.env`:

```bash
nano .env
```

2. Change:

```text
HTTP_PUBLISH_PORT=8092
```

3. Recreate the frontend container:

```bash
docker compose up -d frontend
```

4. Confirm the published port:

```bash
docker compose ps frontend
```

5. Test:

```bash
curl -I http://localhost:8092
```

6. Update firewall rules:

```bash
sudo ufw allow 8092/tcp
```

7. Remove the old firewall rule if it is no longer needed:

```bash
sudo ufw delete allow 8091/tcp
```

## 11. Configure Mission Identity and Branding

For production and pilots, deploy one ERPNext site per mission unless a multi-mission hosting model has been approved. In that model, ERPNext remains the system of record for Company, Customer, Contact, Address, Item, Sales Invoice, Payment Entry, File, Communication, Letter Head, Email Account, Workflow, Role, Dashboard Chart, and Number Card.

First configure ERPNext basics:

1. Company or mission operating entity.
2. Default currency.
3. Default letter head.
4. Email account.
5. Users and roles.
6. Items for consular fees.
7. Payment modes and payment gateways where approved.

Then open ERPNext Desk and search for:

```text
Embassy Settings
```

Complete:

- Embassy / Mission Name
- Embassy Type
- Sending Country
- Host Country
- City
- Address
- Telephone
- Public Email
- Consular Enquiry Email
- Visa Enquiry Email
- Website
- Default Currency
- Default Language
- Additional Languages
- Time Zone
- Appointment Working Days
- Appointment Opening Hours
- Public Holiday List
- Mission Logo
- National Emblem / Coat of Arms Placeholder
- Letter Head
- Email Footer
- Primary Brand Colour
- Secondary Brand Colour
- Online Application URL
- Appointment Booking URL
- Default Payment Mode
- Default Workflow
- Consular Officer in Charge
- Head of Mission
- Data Protection Notice
- Terms and Conditions
- Privacy Notice
- Declaration Text
- Submission Confirmation Text

Use only branding assets supplied and approved by the client mission. Do not commit official flags, coats of arms, or protected government emblems to Git.

## 12. Configure Consular Services

Open:

```text
Consular Service
```

Create one record per service offered by the mission. Examples may include visa, passport service, consular card, attestation, legalisation, civil registry, emergency travel document, or any local service.

Configure:

- Service Name
- Service Code
- Service Category
- Public portal visibility
- Appointment requirement
- Online application requirement
- Document upload requirement
- Payment requirement
- Officer review requirement
- Biometrics or interview requirement
- Default processing time
- Fee Item linked to ERPNext Item
- Default fee and currency
- Validity period
- Service instructions
- Eligibility rules
- Required documents
- Workflow
- Print format
- Email template
- Terms and declaration

Do not hardcode mission-specific services. Use the sample services only as examples.

## 13. Configure Application Form Templates

Open:

```text
Application Form Template
Application Form Section
Application Form Field
Application Form Rule
```

Recommended public application sections:

- Booking
- Personal Details
- Contact Details
- Passport Details
- Travel Details
- Documents
- Review & Submit

Use `Application Form Rule` for configurable behavior:

- Show or hide fields.
- Make fields required.
- Calculate fees.
- Trigger multilingual notices.
- Require documents.
- Require appointments.
- Restrict eligibility.

Keep country-specific rules in configuration. For example, if a nationality, residence country, visa type, or travel purpose changes eligibility, add a rule rather than editing code.

## 14. Configure Document Requirements

For each service, configure required documents in the Consular Service required documents table or in:

```text
Application Document Requirement
```

Use document categories such as:

- Photo
- Passport
- Proof of Address
- Employment Letter
- Invitation Letter
- Flight Ticket
- Yellow Fever Certificate
- Signature
- Other Documents

Configure allowed file types and maximum file size. Uploaded documents link to Frappe `File`; the app does not create duplicate file storage.

Officers review uploaded documents through:

```text
Application Uploaded Document
```

Review statuses:

- Accepted
- Rejected
- Unclear
- Expired
- Missing
- Re-upload Requested

## 15. Configure Fees and Payments

Create ERPNext `Item` records for each payable fee before configuring consular fee rules.

Open:

```text
Consular Fee Rule
Consular Fee Waiver
Consular Payment Review
```

Configure fee matching by:

- Service
- Visa Type
- Nationality
- Residence Country
- Processing Type
- Entry Type
- Fee Item
- Amount
- Currency
- Effective From
- Effective To
- Active

Payments should use ERPNext standard records:

- Sales Invoice
- Payment Entry
- Payment Request
- Mode of Payment

Use `Consular Payment Review` only for embassy-specific review of bank transfer proof, manual confirmation, refund notes, and finance officer audit.

## 16. Configure Appointments

Open:

```text
Appointment Location
Appointment Service Type
Appointment Officer
Appointment Slot
Embassy Appointment
```

Configure:

- Appointment locations and counters.
- Service-specific appointment types.
- Officer assignments.
- Slot dates and times.
- Slot capacity.
- Holiday exclusions.
- Walk-in registration policy.
- Queue number usage.
- External appointment reference if integrating with SimplyBook or another provider later.

The system can operate with internal appointment slots or store references from an external booking provider. It does not depend on any specific provider.

## 17. Configure Users, Roles, and Permissions

Create users and assign roles according to mission policy:

- Applicant
- Consular Officer
- Visa Officer
- Passport Officer
- Appointment Officer
- Cashier / Finance Officer
- Consular Supervisor
- Head of Consular Section
- Head of Mission
- Embassy Administrator
- System Manager

Applicant isolation is enforced through app permission hooks. Applicants should only see their own applications, uploaded document records, and appointments.

Finance users should see payment review and ERPNext finance records. Supervisors and heads of mission should receive only the access needed for review, approval, and reporting.

## 18. Configure Email and Multilingual Content

Configure ERPNext:

```text
Email Account
Email Template
Language
Translation
Letter Head
Notification
```

Included EMS email template categories:

- Registration confirmation
- Application saved
- Application submitted
- Payment pending
- Payment confirmed
- Appointment booked
- Appointment reminder
- Additional documents requested
- Application approved
- Application rejected
- Collection ready
- Dispatch notification

Translate portal labels, public notices, declaration text, privacy notices, email templates, print formats, and service instructions for each supported language.

## 19. Configure Applicant Portal

The public portal routes are:

```text
/embassy
/embassy/requirements
/embassy/apply
/embassy/dashboard
```

Test:

1. Public service list.
2. Requirements checker.
3. Applicant registration and login.
4. Start application.
5. Save draft.
6. Upload documents.
7. Book appointment if required.
8. Submit declaration.
9. Track application status.
10. Applicant-facing messages.

If publishing through a reverse proxy, ensure `FRAPPE_SITE_NAME_HEADER` matches the public hostname.

## 20. Configure Reports and Dashboards

Open the Embassy Management workspace and verify:

- Officer Workbench
- Appointment Calendar
- Embassy Finance Dashboard
- Applications by Service
- Applications by Status
- Applications by Nationality
- Applications by Submission Channel
- Applications by Decision
- Pending Officer Review
- Pending Document Resubmission
- Pending Payments
- Appointments by Day
- No-show Appointments
- Revenue by Service
- Revenue by Month
- Processing Time by Service
- Rejection Reasons
- Officer Workload
- Document Rejection Summary

Dashboard cards cover daily applications, pending review, pending payments, appointments today, urgent cases, and other operational indicators.

## 21. Run a Backup

After setup and initial configuration:

```bash
./scripts/backup-site.sh
```

Backups are written to:

```text
backups/SITE_NAME-YYYYMMDD-HHMMSS
```

Copy backups to approved off-server storage.

## 22. Restore a Backup

Copy backup files to the server, then run:

```bash
./scripts/restore-site.sh \
  --database backups/embassy.example.org-YYYYMMDD-HHMMSS/database.sql.gz \
  --public-files backups/embassy.example.org-YYYYMMDD-HHMMSS/files.tar \
  --private-files backups/embassy.example.org-YYYYMMDD-HHMMSS/private-files.tar
```

Use the actual filenames generated by ERPNext in the backup directory.

## 23. Update the System

Run updates first in staging.

For production:

```bash
./scripts/update-site.sh
```

The script takes a backup before pulling images, rebuilding the backend image, running migrations, and clearing caches.

## 24. Production nginx Reverse Proxy

The repository includes:

```text
nginx/embassy-management.conf
```

Copy it into host nginx and update:

- `server_name`
- TLS certificate paths if HTTPS is added
- Proxy target if `HTTP_PUBLISH_PORT` is not `8091`

Example if ERPNext is published on `8092`:

```nginx
proxy_pass http://127.0.0.1:8092;
```

Then reload nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 25. Useful Operations Commands

Show running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Restart the stack:

```bash
docker compose restart
```

Stop the stack:

```bash
docker compose down
```

Start the stack:

```bash
docker compose up -d
```

Run ERPNext commands:

```bash
docker compose exec backend bench --site "$SITE_NAME" migrate
docker compose exec backend bench --site "$SITE_NAME" clear-cache
```

If `$SITE_NAME` is not loaded in your shell:

```bash
source .env
docker compose exec backend bench --site "$SITE_NAME" clear-cache
```

Create an additional administrator:

```bash
./scripts/create-admin-user.sh admin@example.org Embassy Administrator 'ChangeMe123!'
```

## 26. Troubleshooting

If the site does not open:

```bash
docker compose ps
docker compose logs --tail=100 frontend
docker compose logs --tail=100 backend
```

If the selected host port is busy:

```bash
sudo ss -ltnp | grep ':8091 '
```

Edit `.env`, set another `HTTP_PUBLISH_PORT`, and run:

```bash
docker compose up -d frontend
```

If site creation fails because the database is still starting:

```bash
docker compose ps
docker compose logs --tail=100 mariadb
./scripts/create-site.sh
```

If app installation fails:

```bash
./scripts/install-apps.sh
```

If custom workspace icons, portal CSS, or bundled assets do not display, rebuild the custom image and repair the shared assets volume:

```bash
git pull
docker compose build backend
docker compose run --rm configurator
./scripts/install-apps.sh
./scripts/repair-assets.sh
```

Then refresh the browser with `Ctrl+F5`.

If files do not upload, check disk space and nginx upload size:

```bash
df -h
grep -R "client_max_body_size" nginx /etc/nginx 2>/dev/null || true
```

If background jobs are not running:

```bash
docker compose logs --tail=100 queue-short
docker compose logs --tail=100 queue-long
docker compose logs --tail=100 scheduler
```

If applicants cannot access their applications, check role assignment and applicant profile linkage:

```bash
docker compose exec backend bench --site "$SITE_NAME" console
```

Then inspect:

```python
frappe.get_all("Embassy Applicant Profile", fields=["name", "user", "email"])
```

## 27. Security and Compliance Checklist

- `.env` uses strong passwords.
- HTTPS is enabled for production.
- Firewall allows only required ports.
- Official mission branding is uploaded through ERPNext, not committed to Git.
- Email account is configured with mission-approved SMTP.
- Applicant registration and login policies are approved.
- File type and size limits match mission policy.
- Private files are not publicly exposed.
- Roles have been tested with applicant, officer, finance, supervisor, and head-of-mission accounts.
- Privacy notice, data protection notice, terms, and declaration text are approved.
- Data retention policy is documented.
- Backup completed successfully.
- Restore tested in staging.
- IT administrators know how to run backup, restore, update, sample-data, and asset-repair scripts.

## 28. Go-Live Checklist

- Embassy Settings are complete.
- ERPNext Company, Letter Head, Email Account, Item, Payment Mode, and finance settings are configured.
- Consular services are configured and enabled for the public portal where appropriate.
- Required documents are configured for each service.
- Fee rules are configured and verified by finance.
- Appointment locations, officers, and slots are configured.
- Workflows and approval roles are approved.
- Email templates are reviewed in each supported language.
- Public requirements page is tested.
- Applicant portal is tested on desktop and mobile.
- Officer workbench is tested.
- Payment review process is tested.
- Reports and dashboard cards are visible to the correct roles.
- Backup and restore procedures are tested.
- Production DNS and TLS are active.

## 29. Presentation Sample Data

For demonstrations, load removable `EMSDEMO` generic sample data covering standard consular service catalogue, document requirements, fee rules, and appointment slots:

```bash
./scripts/load-sample-data.sh
```

The sample data is generic and does not imply official government approval.

After presenting, remove only the sample records:

```bash
./scripts/clear-sample-data.sh
```

Both scripts prompt for confirmation. For scripted runs, use `--yes`.
