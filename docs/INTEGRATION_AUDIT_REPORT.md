# A. Integration Audit Report

[Powered by Viewertech](https://viewertech.net)

## Result

The app is designed as an ERPNext/Frappe extension layer. Core ERPNext and Frappe files are not modified.

## Standard DocTypes Used

- Customer, Contact, Address, User, Website User
- File for all uploaded documents
- Communication and Email Template for messaging
- Item, Sales Invoice, Payment Entry, Payment Request, Mode of Payment for fees and payments
- Company, Letter Head, Workflow, Role, Notification, ToDo, Dashboard Chart, Number Card

## Embassy-Specific DocTypes

Embassy Settings, Consular Service, Consular Application, service detail extensions, document requirements, uploaded document review, appointments, fee rules, waivers, payment review, and dynamic form configuration.

## Upgrade Safety

Custom logic lives in `embassy_management`. Hooks use documented extension points: fixtures, scheduler events, permission query conditions, whitelisted methods, and DocType controllers.
