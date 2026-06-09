frappe.pages['officer-workbench'].on_page_load = function (wrapper) {
  const ui = window.embassy_management && window.embassy_management.ui ? window.embassy_management.ui : {
    appIcon: '/assets/embassy_management/img/app_icon.png',
    escape: (value) => frappe.utils.escape_html(value == null ? '' : String(value)),
    icon: () => '',
    statusClass: (value) => String(value || 'open').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''),
    injectDeskStyles: () => {}
  };
  ui.injectDeskStyles();

  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __('Officer Workbench'),
    single_column: true
  });

  const body = $(`
    <div class="ems-desk ems-command-shell">
      <section class="ems-command-header">
        <div class="ems-command-title">
          <span class="ems-brand-mark">
            <img src="${ui.appIcon}" alt="EMS" onerror="this.parentElement.classList.add('ems-brand-mark--fallback'); this.remove();">
          </span>
          <div>
            <div class="ems-kicker">${__('Case Review')}</div>
            <h2>${__('Officer workbench')}</h2>
            <p>${__('Prioritised consular queues with assigned officer, service, status, and decision context.')}</p>
          </div>
        </div>
        <div class="ems-command-actions">
          <div class="ems-toolbar">
            <button class="btn btn-primary ems-refresh" type="button">${ui.icon('refresh-cw', 'sm')} ${__('Refresh')}</button>
            <button class="btn btn-default" type="button" data-route="Consular Application">${ui.icon('plus', 'sm')} ${__('New Case')}</button>
          </div>
          <a href="https://viewertech.net" target="_blank" rel="noopener">Powered by Viewertech</a>
        </div>
      </section>

      <section class="ems-panel">
        <div class="ems-filter-bar">
          <select class="form-control ems-status" aria-label="${__('Status')}">
            <option value="">${__('All active statuses')}</option>
            <option>Submitted</option>
            <option>Payment Confirmed</option>
            <option>Appointment Booked</option>
            <option>Under Initial Review</option>
            <option>Awaiting Additional Documents</option>
            <option>Awaiting Interview</option>
            <option>Under Officer Review</option>
          </select>
          <input class="form-control ems-service" placeholder="${__('Service')}">
          <input class="form-control ems-officer" placeholder="${__('Assigned Officer')}">
        </div>
        <div class="ems-results"></div>
      </section>
    </div>
  `).appendTo(page.body);

  const renderRows = (rows) => {
    if (!rows.length) {
      return `<div class="ems-empty-state">${__('No cases match the current filters.')}</div>`;
    }

    return `
      <div class="ems-list">
        ${rows.map(row => {
          const status = row.application_status || __('No status');
          const priority = row.priority || __('Normal');
          return `
            <a class="ems-list-row" href="/app/consular-application/${encodeURIComponent(row.name)}">
              <span>
                <span class="ems-list-title">${ui.escape(row.application_number || row.name)}</span>
                <span class="ems-list-subtitle">${ui.escape(row.service_label || row.service || __('Service not set'))} &middot; ${ui.escape(row.assigned_officer_label || row.assigned_officer || __('Unassigned'))}</span>
              </span>
              <span class="ems-pill-row">
                <span class="ems-badge ems-badge--${ui.statusClass(priority)}">${ui.escape(priority)}</span>
                <span class="ems-badge ems-badge--${ui.statusClass(status)}">${ui.escape(status)}</span>
              </span>
            </a>
          `;
        }).join('')}
      </div>
    `;
  };

  const render = () => {
    const filters = {};
    const status = body.find('.ems-status').val();
    const service = body.find('.ems-service').val();
    const officer = body.find('.ems-officer').val();
    if (status) filters.application_status = status;
    if (service) filters.service = service;
    if (officer) filters.assigned_officer = officer;

    body.find('.ems-results').html(`<div class="ems-empty-state">${__('Loading cases...')}</div>`);
    frappe.call({
      method: 'embassy_management.embassy_management.page.officer_workbench.officer_workbench.case_queue',
      args: {
        filters,
        limit: 50
      },
      callback: (response) => {
        body.find('.ems-results').html(renderRows(response.message || []));
      },
      error: () => {
        body.find('.ems-results').html(`<div class="ems-empty-state">${__('Unable to load the case queue.')}</div>`);
      }
    });
  };

  body.find('.ems-refresh').on('click', render);
  body.find('[data-route="Consular Application"]').on('click', () => frappe.new_doc('Consular Application'));
  const debouncedRender = frappe.utils.debounce ? frappe.utils.debounce(render, 350) : render;
  body.find('.ems-status, .ems-service, .ems-officer').on('change keyup', debouncedRender);
  render();
};
