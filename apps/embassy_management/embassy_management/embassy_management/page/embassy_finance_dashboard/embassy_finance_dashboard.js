frappe.pages['embassy-finance-dashboard'].on_page_load = function (wrapper) {
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
    title: __('Embassy Finance Dashboard'),
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
            <div class="ems-kicker">${__('Consular Finance')}</div>
            <h2>${__('Payment review and revenue control')}</h2>
            <p>${__('Track bank-transfer evidence, pending confirmations, approved payments, and consular fee activity.')}</p>
          </div>
        </div>
        <div class="ems-command-actions">
          <div class="ems-toolbar">
            <button class="btn btn-primary ems-refresh" type="button">${ui.icon('refresh-cw', 'sm')} ${__('Refresh')}</button>
            <button class="btn btn-default" type="button" data-route="Consular Payment Review">${ui.icon('list', 'sm')} ${__('Payment Reviews')}</button>
          </div>
          <a href="https://viewertech.net" target="_blank" rel="noopener">Powered by Viewertech</a>
        </div>
      </section>
      <section class="ems-results ems-command-shell"></section>
    </div>
  `).appendTo(page.body);

  const renderReviews = (rows) => {
    if (!rows.length) {
      return `<div class="ems-empty-state">${__('No payment reviews found.')}</div>`;
    }

    return `
      <div class="ems-list">
        ${rows.map(row => `
          <a class="ems-list-row" href="/app/consular-payment-review/${encodeURIComponent(row.name)}">
            <span>
              <span class="ems-list-title">${ui.escape(row.application || row.name)}</span>
              <span class="ems-list-subtitle">${ui.escape(row.currency || '')} ${ui.escape(row.amount || 0)}</span>
            </span>
            <span class="ems-badge ems-badge--${ui.statusClass(row.review_status)}">${ui.escape(row.review_status || __('Pending'))}</span>
          </a>
        `).join('')}
      </div>
    `;
  };

  const render = () => {
    body.find('.ems-results').html(`<div class="ems-empty-state">${__('Loading finance dashboard...')}</div>`);
    frappe.call({
      method: 'embassy_management.embassy_management.page.embassy_finance_dashboard.embassy_finance_dashboard.summary',
      callback: (response) => {
        const data = response.message || {};
        const rows = data.reviews || [];
        body.find('.ems-results').html(`
          <section class="ems-metric-grid">
            <article class="ems-metric-card">
              <div class="ems-metric-value">${ui.escape(data.pending || 0)}</div>
              <div class="ems-metric-label">${__('Pending payments')}</div>
            </article>
            <article class="ems-metric-card">
              <div class="ems-metric-value">${ui.escape(data.confirmed || 0)}</div>
              <div class="ems-metric-label">${__('Confirmed payments')}</div>
            </article>
          </section>
          <section class="ems-panel">
            <div class="ems-panel-title">
              <div>
                <h3>${__('Recent Reviews')}</h3>
                <p class="ems-panel-copy">${__('Latest consular payment review records.')}</p>
              </div>
            </div>
            ${renderReviews(rows)}
          </section>
        `);
      },
      error: () => {
        body.find('.ems-results').html(`<div class="ems-empty-state">${__('Unable to load finance summary.')}</div>`);
      }
    });
  };

  body.find('.ems-refresh').on('click', render);
  body.find('[data-route="Consular Payment Review"]').on('click', () => frappe.set_route('List', 'Consular Payment Review'));
  render();
};
