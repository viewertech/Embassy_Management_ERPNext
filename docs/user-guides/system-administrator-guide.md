# System Administrator Guide

[Powered by Viewertech](https://viewertech.net)

This guide is for IT administrators responsible for deployment, configuration, access control, backups, updates, and security.

## Deployment

Use the full Ubuntu guide:

```text
docs/ubuntu-full-setup-guide.md
```

The recommended production host port is `8091` for the current server because `8080` and `8090` are already in use.

## Environment File

Configure:

```text
.env
```

Important values:

- SITE_NAME
- FRAPPE_SITE_NAME_HEADER
- ADMIN_PASSWORD
- DB_ROOT_PASSWORD
- MYSQL_ROOT_PASSWORD
- MARIADB_ROOT_PASSWORD
- HTTP_PUBLISH_PORT
- INSTALL_APPS
- BACKUP_DIR
- BACKUP_RETENTION_DAYS

Use strong generated passwords and keep `.env` out of Git.

## Site Operations

Create or repair the site:

```bash
./scripts/create-site.sh
./scripts/install-apps.sh
./scripts/repair-assets.sh
```

Update:

```bash
./scripts/update-site.sh
```

Backup:

```bash
./scripts/backup-site.sh
```

Restore:

```bash
./scripts/restore-site.sh --database path/to/database.sql.gz
```

## Users And Roles

Create users in ERPNext and assign only the roles needed:

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

Test each role with a non-administrator account before go-live.

## Security Checklist

- Enforce HTTPS in production.
- Configure SMTP with approved mission account.
- Keep private files private.
- Review file type and size limits.
- Use strong passwords.
- Restrict System Manager access.
- Test applicant data isolation.
- Schedule off-server backups.
- Test restore in staging.
- Document data retention policy.

## Demo Data

Load demo data only in a demo or pilot environment:

```bash
./scripts/load-sample-data.sh
```

Remove demo data:

```bash
./scripts/clear-sample-data.sh
```

Do not load sample data into production without written approval.
