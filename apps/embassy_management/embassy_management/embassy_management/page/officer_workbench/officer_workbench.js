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

  const quickFilters = {
    mine: false,
    urgent: false
  };

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
          <select class="form-control ems-priority" aria-label="${__('Priority')}">
            <option value="">${__('Any priority')}</option>
            <option>Normal</option>
            <option>Urgent</option>
            <option>Emergency</option>
          </select>
          <input class="form-control ems-service" placeholder="${__('Type service name')}">
          <input class="form-control ems-officer" placeholder="${__('Type officer name or email')}">
          <button class="btn btn-default ems-mine" type="button">${ui.icon('user-check', 'sm')} ${__('Mine')}</button>
          <button class="btn btn-default ems-urgent" type="button">${ui.icon('alert-triangle', 'sm')} ${__('Urgent')}</button>
          <button class="btn btn-default ems-clear" type="button">${ui.icon('x', 'sm')} ${__('Clear')}</button>
        </div>
        <div class="ems-results"></div>
      </section>
    </div>
  `).appendTo(page.body);

  const renderRows = (rows) => {
    if (!rows.length) {
      return `
        <div class="ems-empty-state">
          <div>
            <strong>${__('No matching cases')}</strong>
            <p>${__('Try a broader status, clear the filters, or create a new case.')}</p>
            <div class="ems-empty-actions">
              <button class="btn btn-primary" type="button" data-empty-action="new-case">${ui.icon('plus', 'sm')} ${__('New Case')}</button>
              <button class="btn btn-default" type="button" data-empty-action="clear">${ui.icon('x', 'sm')} ${__('Clear Filters')}</button>
            </div>
          </div>
        </div>
      `;
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
    const priority = body.find('.ems-priority').val();
    const service = body.find('.ems-service').val();
    const officer = body.find('.ems-officer').val();
    if (status) filters.application_status = status;
    if (priority) filters.priority = priority;
    if (quickFilters.urgent) filters.priority = ['in', ['Urgent', 'Emergency']];
    if (quickFilters.mine) filters.assigned_officer = frappe.session.user;

    body.find('.ems-results').html(`<div class="ems-empty-state">${__('Loading cases...')}</div>`);
    frappe.call({
      method: 'embassy_management.embassy_management.page.officer_workbench.officer_workbench.case_queue',
      args: {
        filters,
        service_query: service,
        officer_query: officer,
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
  body.on('click', '[data-empty-action="new-case"]', () => frappe.new_doc('Consular Application'));
  body.on('click', '[data-empty-action="clear"]', () => clearFilters());
  body.find('.ems-mine').on('click', function () {
    quickFilters.mine = !quickFilters.mine;
    $(this).toggleClass('btn-primary', quickFilters.mine).toggleClass('btn-default', !quickFilters.mine);
    render();
  });
  body.find('.ems-urgent').on('click', function () {
    quickFilters.urgent = !quickFilters.urgent;
    $(this).toggleClass('btn-primary', quickFilters.urgent).toggleClass('btn-default', !quickFilters.urgent);
    render();
  });
  body.find('.ems-clear').on('click', () => clearFilters());
  const debouncedRender = frappe.utils.debounce ? frappe.utils.debounce(render, 350) : render;
  body.find('.ems-status, .ems-priority, .ems-service, .ems-officer').on('change keyup', debouncedRender);

  function clearFilters() {
    quickFilters.mine = false;
    quickFilters.urgent = false;
    body.find('.ems-status, .ems-priority, .ems-service, .ems-officer').val('');
    body.find('.ems-mine, .ems-urgent').removeClass('btn-primary').addClass('btn-default');
    render();
  }

  render();
};
