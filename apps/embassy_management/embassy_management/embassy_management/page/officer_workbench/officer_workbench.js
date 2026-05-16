frappe.pages['officer-workbench'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __('Officer Workbench'),
    single_column: true
  });

  const body = $(`
    <div class="ems-desk-page">
      <div class="row mb-3">
        <div class="col-md-3"><select class="form-control ems-status">
          <option value="">${__('All active statuses')}</option>
          <option>Submitted</option>
          <option>Payment Confirmed</option>
          <option>Appointment Booked</option>
          <option>Under Initial Review</option>
          <option>Awaiting Additional Documents</option>
          <option>Awaiting Interview</option>
          <option>Under Officer Review</option>
        </select></div>
        <div class="col-md-3"><input class="form-control ems-service" placeholder="${__('Service')}"></div>
        <div class="col-md-3"><input class="form-control ems-officer" placeholder="${__('Assigned Officer')}"></div>
        <div class="col-md-3"><button class="btn btn-primary ems-refresh">${__('Refresh')}</button></div>
      </div>
      <div class="ems-results"></div>
    </div>
  `).appendTo(page.body);

  const render = () => {
    const filters = {};
    const status = body.find('.ems-status').val();
    const service = body.find('.ems-service').val();
    const officer = body.find('.ems-officer').val();
    if (status) filters.application_status = status;
    if (service) filters.service = service;
    if (officer) filters.assigned_officer = officer;
    frappe.call({
      method: 'frappe.client.get_list',
      args: {
        doctype: 'Consular Application',
        fields: ['name', 'application_number', 'service', 'application_status', 'priority', 'assigned_officer', 'modified'],
        filters,
        limit_page_length: 50,
        order_by: 'modified asc'
      },
      callback: (response) => {
        const rows = response.message || [];
        body.find('.ems-results').html(`
          <div class="list-group">
            ${rows.map(row => `
              <a class="list-group-item list-group-item-action" href="/app/consular-application/${encodeURIComponent(row.name)}">
                <div class="d-flex justify-content-between">
                  <strong>${frappe.utils.escape_html(row.application_number || row.name)}</strong>
                  <span>${frappe.utils.escape_html(row.priority || '')}</span>
                </div>
                <div>${frappe.utils.escape_html(row.service || '')} - ${frappe.utils.escape_html(row.application_status || '')}</div>
                <small>${frappe.utils.escape_html(row.assigned_officer || __('Unassigned'))}</small>
              </a>
            `).join('')}
          </div>
        `);
      }
    });
  };

  body.find('.ems-refresh').on('click', render);
  render();
};
