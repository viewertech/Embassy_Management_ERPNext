frappe.pages['appointment-calendar'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __('Appointment Calendar'),
    single_column: true
  });

  const body = $(`<div class="ems-desk-page"><button class="btn btn-primary mb-3 ems-refresh">${__('Refresh')}</button><div class="ems-results"></div></div>`).appendTo(page.body);

  const render = () => {
    frappe.call({
      method: 'embassy_management.embassy_management.page.appointment_calendar.appointment_calendar.upcoming',
      callback: (response) => {
        const rows = response.message || [];
        body.find('.ems-results').html(`
          <div class="table-responsive">
            <table class="table table-bordered">
              <thead><tr><th>${__('Date')}</th><th>${__('Time')}</th><th>${__('Booking')}</th><th>${__('Service')}</th><th>${__('Location')}</th><th>${__('Status')}</th></tr></thead>
              <tbody>
                ${rows.map(row => `
                  <tr>
                    <td>${frappe.utils.escape_html(row.appointment_date || '')}</td>
                    <td>${frappe.utils.escape_html(row.start_time || '')}</td>
                    <td><a href="/app/embassy-appointment/${encodeURIComponent(row.name)}">${frappe.utils.escape_html(row.booking_code || row.name)}</a></td>
                    <td>${frappe.utils.escape_html(row.service || '')}</td>
                    <td>${frappe.utils.escape_html(row.location || '')}</td>
                    <td>${frappe.utils.escape_html(row.status || '')}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `);
      }
    });
  };

  body.find('.ems-refresh').on('click', render);
  render();
};
