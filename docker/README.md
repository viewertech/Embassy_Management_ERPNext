# Docker Notes

[Powered by Viewertech](https://viewertech.net)

This repository builds a custom image from the official ERPNext v16 image and copies the local `embassy_management` app into `/home/frappe/frappe-bench/apps/embassy_management`.

The image keeps Frappe and ERPNext core unchanged. Site creation and app installation are done through the scripts in `/scripts`.
