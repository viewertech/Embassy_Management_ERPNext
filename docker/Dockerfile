ARG ERPNEXT_VERSION=v16
FROM frappe/erpnext:${ERPNEXT_VERSION}

USER root
COPY apps/embassy_management /home/frappe/frappe-bench/apps/embassy_management
COPY sample_data /home/frappe/frappe-bench/sample_data
RUN chown -R frappe:frappe /home/frappe/frappe-bench/apps/embassy_management /home/frappe/frappe-bench/sample_data

USER frappe
RUN cd /home/frappe/frappe-bench && \
    ./env/bin/pip install --no-cache-dir --editable apps/embassy_management && \
    ./env/bin/python -c "import embassy_management; print('Installed embassy_management', embassy_management.__version__)" && \
    mkdir -p assets && \
    if [ -L assets/embassy_management ] || [ -f assets/embassy_management ]; then rm -f assets/embassy_management; elif [ -d assets/embassy_management ]; then mv assets/embassy_management assets/embassy_management.bak; fi && \
    ln -s ../apps/embassy_management/embassy_management/public assets/embassy_management && \
    if ! grep -qx "embassy_management" sites/apps.txt 2>/dev/null; then echo "embassy_management" >> sites/apps.txt; fi
