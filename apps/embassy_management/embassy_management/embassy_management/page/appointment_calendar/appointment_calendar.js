frappe.pages['appointment-calendar'].on_page_load = function (wrapper) {
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
    title: __('Appointment Calendar'),
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
            <div class="ems-kicker">${__('Appointments')}</div>
            <h2>${__('Consular appointment calendar')}</h2>
            <p>${__('Upcoming bookings, service counters, interview rooms, statuses, walk-ins, and no-show follow-up.')}</p>
          </div>
        </div>
        <div class="ems-command-actions">
          <div class="ems-toolbar">
            <button class="btn btn-primary ems-refresh" type="button" title="${__('Reload appointments using the current filters')}">${ui.icon('refresh-cw', 'sm')} ${__('Refresh')}</button>
            <button class="btn btn-default" type="button" data-route="Embassy Appointment" title="${__('Create a new appointment or walk-in booking')}">${ui.icon('plus', 'sm')} ${__('New Appointment')}</button>
          </div>
          <a href="https://viewertech.net" target="_blank" rel="noopener">Powered by Viewertech</a>
        </div>
      </section>
      <section class="ems-panel">
        <div class="ems-panel-title">
          <div>
            <h3>${__('Upcoming Appointments')}</h3>
            <p class="ems-panel-copy">${__('Sorted by appointment date and start time.')}</p>
          </div>
        </div>
        <div class="ems-filter-bar">
          <input class="form-control ems-from-date" type="date" aria-label="${__('From date')}">
          <input class="form-control ems-to-date" type="date" aria-label="${__('To date')}">
          <select class="form-control ems-status" aria-label="${__('Status')}">
            <option value="">${__('Any status')}</option>
            <option>Booked</option>
            <option>Confirmed</option>
            <option>Rescheduled</option>
            <option>Completed</option>
            <option>No-show</option>
            <option>Cancelled</option>
            <option>Walk-in</option>
          </select>
          <input class="form-control ems-service" placeholder="${__('Type service name')}">
          <input class="form-control ems-location" placeholder="${__('Type location name')}">
          <button class="btn btn-default ems-today" type="button" title="${__('Show appointments for today')}">${ui.icon('calendar', 'sm')} ${__('Today')}</button>
          <button class="btn btn-default ems-clear" type="button" title="${__('Clear appointment filters')}">${ui.icon('x', 'sm')} ${__('Clear')}</button>
        </div>
        <div class="ems-results"></div>
      </section>
    </div>
  `).appendTo(page.body);

  const renderTable = (rows) => {
    if (!rows.length) {
      return `
        <div class="ems-empty-state">
          <div>
            <strong>${__('No appointments found')}</strong>
            <p>${__('Clear the filters, create appointment slots, or add a walk-in appointment.')}</p>
            <div class="ems-empty-actions">
              <button class="btn btn-primary" type="button" data-empty-action="new-appointment" title="${__('Create a new appointment record')}">${ui.icon('plus', 'sm')} ${__('New Appointment')}</button>
              <button class="btn btn-default" type="button" data-empty-action="slots" title="${__('Open appointment slot setup')}">${ui.icon('calendar-plus', 'sm')} ${__('Appointment Slots')}</button>
              <button class="btn btn-default" type="button" data-empty-action="clear" title="${__('Remove all appointment filters')}">${ui.icon('x', 'sm')} ${__('Clear Filters')}</button>
            </div>
          </div>
        </div>
      `;
    }

    return `
      <div class="ems-table-wrap table-responsive">
        <table class="table ems-table">
          <thead>
            <tr>
              <th>${__('Date')}</th>
              <th>${__('Time')}</th>
              <th>${__('Booking')}</th>
              <th>${__('Service')}</th>
              <th>${__('Location')}</th>
              <th>${__('Status')}</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map(row => `
              <tr>
                <td>${ui.escape(row.appointment_date || '')}</td>
                <td>${ui.escape(row.start_time || '')}</td>
                <td><a href="/app/embassy-appointment/${encodeURIComponent(row.name)}">${ui.escape(row.booking_code || row.name)}</a></td>
                <td>${ui.escape(row.service_label || row.service || '')}</td>
                <td>${ui.escape(row.location_label || row.location || '')}</td>
                <td><span class="ems-badge ems-badge--${ui.statusClass(row.status)}">${ui.escape(row.status || '')}</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  };

  const render = () => {
    body.find('.ems-results').html(`<div class="ems-empty-state">${__('Loading appointments...')}</div>`);
    frappe.call({
      method: 'embassy_management.embassy_management.page.appointment_calendar.appointment_calendar.upcoming',
      args: {
        from_date: body.find('.ems-from-date').val(),
        to_date: body.find('.ems-to-date').val(),
        status: body.find('.ems-status').val(),
        service_query: body.find('.ems-service').val(),
        location_query: body.find('.ems-location').val()
      },
      callback: (response) => {
        body.find('.ems-results').html(renderTable(response.message || []));
      },
      error: () => {
        body.find('.ems-results').html(`<div class="ems-empty-state">${__('Unable to load appointments.')}</div>`);
      }
    });
  };

  body.find('.ems-refresh').on('click', render);
  body.find('[data-route="Embassy Appointment"]').on('click', () => frappe.new_doc('Embassy Appointment'));
  body.find('.ems-today').on('click', () => {
    const today = frappe.datetime && frappe.datetime.get_today ? frappe.datetime.get_today() : new Date().toISOString().slice(0, 10);
    body.find('.ems-from-date, .ems-to-date').val(today);
    render();
  });
  body.find('.ems-clear').on('click', () => clearFilters());
  body.on('click', '[data-empty-action="new-appointment"]', () => frappe.new_doc('Embassy Appointment'));
  body.on('click', '[data-empty-action="slots"]', () => frappe.set_route('List', 'Appointment Slot'));
  body.on('click', '[data-empty-action="clear"]', () => clearFilters());
  const debouncedRender = frappe.utils.debounce ? frappe.utils.debounce(render, 350) : render;
  body.find('.ems-from-date, .ems-to-date, .ems-status, .ems-service, .ems-location').on('change keyup', debouncedRender);

  function clearFilters() {
    body.find('.ems-from-date, .ems-to-date, .ems-status, .ems-service, .ems-location').val('');
    render();
  }

  render();
};
