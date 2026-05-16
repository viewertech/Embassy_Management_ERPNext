frappe.pages['embassy-finance-dashboard'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __('Embassy Finance Dashboard'),
    single_column: true
  });

  const body = $(`<div class="ems-desk-page"><button class="btn btn-primary mb-3 ems-refresh">${__('Refresh')}</button><div class="ems-results"></div></div>`).appendTo(page.body);

  const render = () => {
    frappe.call({
      method: 'embassy_management.embassy_management.page.embassy_finance_dashboard.embassy_finance_dashboard.summary',
      callback: (response) => {
        const data = response.message || {};
        const rows = data.reviews || [];
        body.find('.ems-results').html(`
          <div class="row mb-3">
            <div class="col-md-4"><div class="card p-3"><h3>${data.pending || 0}</h3><p>${__('Pending payments')}</p></div></div>
            <div class="col-md-4"><div class="card p-3"><h3>${data.confirmed || 0}</h3><p>${__('Confirmed payments')}</p></div></div>
          </div>
          <div class="list-group">
            ${rows.map(row => `
              <a class="list-group-item list-group-item-action" href="/app/consular-payment-review/${encodeURIComponent(row.name)}">
                <div class="d-flex justify-content-between">
                  <strong>${frappe.utils.escape_html(row.application || '')}</strong>
                  <span>${frappe.format(row.amount || 0, { fieldtype: 'Currency', options: 'currency' }, { currency: row.currency })}</span>
                </div>
                <small>${frappe.utils.escape_html(row.review_status || '')}</small>
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
