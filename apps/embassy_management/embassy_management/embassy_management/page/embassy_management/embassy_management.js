frappe.pages['embassy-management'].on_page_load = function (wrapper) {
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
    title: __('Embassy Management'),
    single_column: true
  });

  const cards = [
    {
      icon: 'file-text',
      label: __('Consular Applications'),
      description: __('Submitted, draft, urgent, approved, rejected, and completed cases.'),
      meta: __('Case registry'),
      action: () => frappe.set_route('List', 'Consular Application')
    },
    {
      icon: 'users',
      label: __('Officer Workbench'),
      description: __('Assigned queues, review actions, document follow-up, and decisions.'),
      meta: __('Review queue'),
      action: () => frappe.set_route('officer-workbench')
    },
    {
      icon: 'calendar',
      label: __('Appointments'),
      description: __('Bookings, walk-ins, no-shows, slots, services, and locations.'),
      meta: __('Calendar'),
      action: () => frappe.set_route('List', 'Embassy Appointment')
    },
    {
      icon: 'settings',
      label: __('Consular Services'),
      description: __('Service catalogue, requirements, fees, rules, templates, and branding.'),
      meta: __('Configuration'),
      action: () => frappe.set_route('List', 'Consular Service')
    },
    {
      icon: 'credit-card',
      label: __('Finance Dashboard'),
      description: __('Payment reviews, fee evidence, revenue checks, and confirmations.'),
      meta: __('Payments'),
      action: () => frappe.set_route('embassy-finance-dashboard')
    },
    {
      icon: 'external-link',
      label: __('Applicant Portal'),
      description: __('Public requirements, online applications, dashboard, and tracking.'),
      meta: __('Public portal'),
      action: () => window.open('/embassy', '_blank', 'noopener')
    }
  ];

  const metrics = [
    { label: __('Total Applications'), selector: 'applications', doctype: 'Consular Application' },
    {
      label: __('Pending Review'),
      selector: 'review',
      doctype: 'Consular Application',
      filters: { application_status: ['in', ['Submitted', 'Under Initial Review', 'Under Officer Review']] }
    },
    { label: __('Appointments'), selector: 'appointments', doctype: 'Embassy Appointment' },
    { label: __('Payment Reviews'), selector: 'payments', doctype: 'Consular Payment Review' }
  ];

  const body = $(`
    <div class="ems-desk ems-command-shell">
      <section class="ems-command-header">
        <div class="ems-command-title">
          <span class="ems-brand-mark">
            <img src="${ui.appIcon}" alt="EMS" onerror="this.parentElement.classList.add('ems-brand-mark--fallback'); this.remove();">
          </span>
          <div>
            <div class="ems-kicker">${__('Embassy Management ERPNext')}</div>
            <h2>${__('Consular operations command center')}</h2>
            <p>${__('A reusable ERPNext layer for applications, appointments, documents, payments, officer review, reporting, and applicant self-service.')}</p>
          </div>
        </div>
        <div class="ems-command-actions">
          <div class="ems-pill-row">
            <span class="ems-pill">${ui.icon('shield', 'sm')} ${__('Upgrade-safe')}</span>
            <span class="ems-pill">${ui.icon('globe', 'sm')} ${__('Multilingual')}</span>
            <span class="ems-pill">${ui.icon('lock', 'sm')} ${__('Role-based')}</span>
          </div>
          <div class="ems-toolbar">
            <button class="btn btn-primary" type="button" data-action="portal">${ui.icon('external-link', 'sm')} ${__('Open Portal')}</button>
            <button class="btn btn-default" type="button" data-action="settings">${ui.icon('settings', 'sm')} ${__('Embassy Settings')}</button>
          </div>
          <a href="https://viewertech.net" target="_blank" rel="noopener">Powered by Viewertech</a>
        </div>
      </section>

      <section class="ems-metric-grid">
        ${metrics.map(metric => `
          <article class="ems-metric-card">
            <div class="ems-metric-value" data-metric="${metric.selector}">-</div>
            <div class="ems-metric-label">${ui.escape(metric.label)}</div>
          </article>
        `).join('')}
      </section>

      <section class="ems-action-grid">
        ${cards.map((card, index) => `
          <button class="ems-action-card" type="button" data-index="${index}">
            <span class="ems-card-head">
              <span class="ems-card-icon">${ui.icon(card.icon, 'md')}</span>
              <strong>${ui.escape(card.label)}</strong>
            </span>
            <span class="ems-card-copy">${ui.escape(card.description)}</span>
            <span class="ems-card-meta">${ui.escape(card.meta)} ${ui.icon('chevron-right', 'sm')}</span>
          </button>
        `).join('')}
      </section>

      <section class="ems-panel">
        <div class="ems-panel-title">
          <div>
            <h3>${__('Operational Setup')}</h3>
            <p class="ems-panel-copy">${__('Core records used by every mission implementation.')}</p>
          </div>
        </div>
        <div class="ems-action-grid">
          ${[
            ['Embassy Settings', 'settings', __('Mission profile, branding, language, currency, notices, and defaults.')],
            ['Application Form Template', 'list', __('Dynamic application sections, fields, rules, and declarations.')],
            ['Consular Fee Rule', 'credit-card', __('Nationality, visa type, processing type, entry type, and waiver rules.')],
            ['Appointment Slot', 'calendar', __('Capacity, locations, officers, working days, and public holiday control.')]
          ].map((item) => `
            <button class="ems-action-card" type="button" data-doctype="${ui.escape(item[0])}">
              <span class="ems-card-head">
                <span class="ems-card-icon">${ui.icon(item[1], 'md')}</span>
                <strong>${ui.escape(__(item[0]))}</strong>
              </span>
              <span class="ems-card-copy">${ui.escape(item[2])}</span>
              <span class="ems-card-meta">${__('Open list')} ${ui.icon('chevron-right', 'sm')}</span>
            </button>
          `).join('')}
        </div>
      </section>
    </div>
  `).appendTo(page.body);

  body.find('.ems-action-card[data-index]').on('click', function () {
    cards[Number($(this).data('index'))].action();
  });

  body.find('.ems-action-card[data-doctype]').on('click', function () {
    frappe.set_route('List', $(this).data('doctype'));
  });

  body.find('[data-action="portal"]').on('click', () => window.open('/embassy', '_blank', 'noopener'));
  body.find('[data-action="settings"]').on('click', () => frappe.set_route('Form', 'Embassy Settings', 'Embassy Settings'));

  metrics.forEach((metric) => {
    frappe.call({
      method: 'frappe.client.get_count',
      args: {
        doctype: metric.doctype,
        filters: metric.filters || {}
      },
      callback: (response) => {
        body.find(`[data-metric="${metric.selector}"]`).text(response.message || 0);
      },
      error: () => {
        body.find(`[data-metric="${metric.selector}"]`).text('0');
      }
    });
  });
};
