# Embassy Management ERPNext User Guides

[Powered by Viewertech](https://viewertech.net)

These guides are written for embassy, high commission, consulate, and diplomatic mission pilot and production users. They separate standard ERPNext/Frappe operations from the Embassy Management extension layer.

## Which Guide To Use

- [Applicant Portal Guide](applicant-portal-guide.md): registration, requirements checks, applications, documents, appointments, payments, and tracking.
- [Consular Officer Guide](consular-officer-guide.md): case queues, application review, document review, applicant messaging, decisions, and completion.
- [Appointment Officer Guide](appointment-officer-guide.md): appointment locations, service types, officer calendars, slots, bookings, rescheduling, cancellations, no-shows, walk-ins, and queues.
- [Finance Officer Guide](finance-officer-guide.md): fee rules, Sales Invoices, Payment Entries, bank transfer proof, payment reviews, waivers, refunds, and revenue reports.
- [Consular Supervisor and Head of Mission Guide](supervisor-head-of-mission-guide.md): approvals, escalations, dashboards, performance reporting, governance, and oversight.
- [System Administrator Guide](system-administrator-guide.md): deployment operations, mission settings, branding, users, roles, backups, restore, updates, demo data, and security.

## Word Versions

Client-ready Word versions of these staff guides are generated in:

```text
docs/user-guides/docx
```

After editing any Markdown guide, regenerate the Word documents. The same command also refreshes the top-level operational guide documents in `docs/docx`.

```bash
python scripts/generate-user-guide-docx.py
```

## Workspace Rule

Use **ERPNext/Frappe** for standard system-of-record operations:

- Customer, Contact, Address, User, Website User
- File, Communication, Email Template, Notification
- Company, Item, Sales Invoice, Payment Entry, Payment Request, Mode of Payment
- Role, Workflow, Workflow State, Workflow Action
- Letter Head, Web Form, ToDo, Dashboard Chart, Number Card

Use **Embassy Management** for diplomatic mission controls:

- Mission settings and public branding
- Consular service catalogue
- Consular applications and service-specific extensions
- Dynamic application form templates and rules
- Document requirements and officer review
- Appointment slots, booking codes, and queue support
- Consular fee rules, waivers, and payment review
- Officer workbench, dashboards, and consular reports

## Demo Data

For presentations, IT can load removable `EMSDEMO` records:

```bash
./scripts/load-sample-data.sh
```

After presenting, IT can remove the demo records:

```bash
./scripts/clear-sample-data.sh
```

Never load demo data into a live production site without written approval from the mission.
