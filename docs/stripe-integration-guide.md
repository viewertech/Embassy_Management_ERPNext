# Stripe Integration Guide

Embassy Management uses Stripe Checkout for hosted card payments. Applicants are redirected to Stripe, and EMS stores only payment references and review status.

Powered by [Viewertech](https://viewertech.net).

## Configure Embassy Settings

Open **Embassy Settings** and complete the **Stripe Payments** section:

- Enable Stripe Checkout
- Stripe Mode: Test or Live
- Stripe Publishable Key
- Stripe Secret Key
- Stripe Webhook Secret
- Stripe Success URL, optional
- Stripe Cancel URL, optional

Default URLs are generated from the ERPNext site URL when custom URLs are blank.

## Stripe Webhook

Create a Stripe webhook endpoint pointing to:

```text
https://your-site.example.com/api/method/embassy_management.api.stripe_payments.stripe_webhook
```

Subscribe to:

- `checkout.session.completed`
- `checkout.session.expired`
- `payment_intent.payment_failed`

Copy the Stripe webhook signing secret into **Embassy Settings > Stripe Webhook Secret**.

## Applicant Payment Flow

1. Applicant opens the public portal dashboard.
2. Applicant clicks **Pay with Stripe** on an unpaid application.
3. EMS creates or reuses the ERPNext Sales Invoice.
4. EMS creates a Stripe Checkout Session.
5. Stripe redirects the applicant to hosted Checkout.
6. Stripe sends a webhook back to EMS.
7. EMS marks the application/payment review as confirmed, expired, or failed.

## Notes

- ERPNext remains the system of record for applications, customers, invoices, and payment reviews.
- Stripe keys are stored in Embassy Settings password fields.
- Payment Entry creation can be added later when the mission's Stripe clearing account and bank reconciliation process are confirmed.
- Test mode should be used before enabling live card payments.
- The integration uses Stripe Checkout Sessions and verifies signed webhook payloads before updating EMS records.
