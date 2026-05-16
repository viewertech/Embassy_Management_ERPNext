ARG ERPNEXT_VERSION=v16
FROM frappe/erpnext:${ERPNEXT_VERSION}

USER root
COPY apps/embassy_management /home/frappe/frappe-bench/apps/embassy_management
COPY sample_data /home/frappe/frappe-bench/sample_data
RUN chown -R frappe:frappe /home/frappe/frappe-bench/apps/embassy_management /home/frappe/frappe-bench/sample_data

USER frappe
RUN cd /home/frappe/frappe-bench && \
    if ! grep -qx "embassy_management" sites/apps.txt 2>/dev/null; then echo "embassy_management" >> sites/apps.txt; fi
