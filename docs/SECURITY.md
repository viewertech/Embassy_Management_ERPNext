# Security and Compliance Guide

[Powered by Viewertech](https://viewertech.net)

## Implemented Controls

- Role-based permissions for applicants, officers, supervisors, finance, administrators, and heads of mission.
- Permission query conditions isolate applicant applications, uploaded document records, and appointments.
- Uploaded files link to Frappe File; the app does not implement parallel file storage.
- Document review keeps reviewed by, reviewed on, status, notes, and child log rows.
- Privacy, terms, and declaration acceptance are logged on submission.

## Required Production Hardening

- Enforce HTTPS.
- Configure secure SMTP.
- Set file upload limits at nginx, Frappe, and operating-system level.
- Review allowed file types per service.
- Enable rate limiting for public endpoints at the reverse proxy.
- Enable login throttling and strong password policy.
- Schedule encrypted offsite backups and test restore.
- Define data retention and deletion rules per mission policy.
