# B. Duplication Risk Report

[Powered by Viewertech](https://viewertech.net)

## Low Risk

The app links to ERPNext/Frappe masters rather than recreating them.

## Watch Items

- Embassy Applicant Profile must remain a consular profile and must not become a duplicate Customer, Contact, or Address master.
- Application Uploaded Document must link to File and must not store binary files.
- Consular Payment Review must remain a review overlay and must not replace Sales Invoice or Payment Entry.
- Application Form Template must not be used to replace Frappe Web Form where standard Web Form is sufficient.

## Controls

Permission hooks, links to standard DocTypes, and docs reinforce the intended boundaries.
