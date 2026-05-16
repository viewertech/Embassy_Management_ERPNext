# Deployment Guide

[Powered by Viewertech](https://viewertech.net)

This guide targets Ubuntu 24.04 LTS, Docker Compose, ERPNext v16, Frappe v16, and the `embassy_management` custom app.

## Steps

1. Clone the repository.
2. Copy `.env.example` to `.env` and change all passwords.
3. Run `./scripts/install.sh`.
4. Run `docker compose build`.
5. Run `./scripts/create-site.sh`.
6. Start the stack with `docker compose up -d`.
7. Configure DNS and reverse proxy using `nginx/embassy-management.conf`.
8. Enable HTTPS with your preferred ACME client.

## Production Notes

- Store database and site volumes on encrypted disks where required by policy.
- Configure SMTP in ERPNext Email Account.
- Configure Payment Gateway and Payment Request only after finance approval.
- Keep private files private and review nginx upload limits.
- Schedule `backup-site.sh` through cron or your platform scheduler.
