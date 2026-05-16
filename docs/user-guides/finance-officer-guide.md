# Finance Officer Guide

[Powered by Viewertech](https://viewertech.net)

This guide is for cashier, finance, and payment-review users.

## Standard ERPNext Finance Records

Use ERPNext as the system of record for:

- Item
- Sales Invoice
- Payment Entry
- Payment Request
- Mode of Payment
- Customer

Embassy Management adds fee rules, waivers, and payment review records only for consular-specific workflow.

## Configure Fee Items

Create one ERPNext Item per payable consular fee. Use clear item names and income accounts approved by finance.

Link the item from:

```text
Consular Service
Consular Fee Rule
```

## Configure Fee Rules

Open:

```text
Consular Fee Rule
```

Configure matching by service, visa type, nationality, residence country, processing type, entry type, amount, currency, and effective dates.

Use fee rules for normal, fast-track, emergency, reduced-fee, and country-specific policies. Keep every policy configurable.

## Create And Review Invoices

From a Consular Application, create a Sales Invoice where payment is required. Confirm:

- Customer
- Fee item
- Amount
- Currency
- Posting date
- Taxes if applicable

Use Payment Entry for confirmed payments. Use Payment Request only where an approved online gateway is configured.

## Review Manual Payment Proof

Open:

```text
Consular Payment Review
```

Review proof of payment, bank transfer reference, amount, currency, linked Sales Invoice, and linked Payment Entry.

Set review status:

- Pending
- Confirmed
- Rejected
- Refunded

Add review notes for audit.

## Waivers And Refunds

Use:

```text
Consular Fee Waiver
```

Record reason, amount, currency, approval user, and approval date. Refunds should be reconciled through standard ERPNext finance records and documented in Consular Payment Review.

## Finance Reports

Use reports:

- Pending Payments
- Revenue by Service
- Revenue by Month
- Consular Payment Review list
- Sales Invoice reports
- Payment Entry reports

Finance should reconcile EMS reports against ERPNext accounting reports before sign-off.
