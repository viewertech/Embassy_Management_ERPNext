frappe.pages['appointment-calendar'].on_page_load = function (wrapper) {
  const ui = window.embassy_management && embassy_management.ui ? embassy_management.ui : {
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
            <button class="btn btn-primary ems-refresh" type="button">${ui.icon('refresh-cw', 'sm')} ${__('Refresh')}</button>
            <button class="btn btn-default" type="button" data-route="Embassy Appointment">${ui.icon('plus', 'sm')} ${__('New Appointment')}</button>
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
        <div class="ems-results"></div>
      </section>
    </div>
  `).appendTo(page.body);

  const renderTable = (rows) => {
    if (!rows.length) {
      return `<div class="ems-empty-state">${__('No upcoming appointments found.')}</div>`;
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
                <td>${ui.escape(row.service || '')}</td>
                <td>${ui.escape(row.location || '')}</td>
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
  render();
};
