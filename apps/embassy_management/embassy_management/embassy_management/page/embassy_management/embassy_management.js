frappe.pages['embassy-management'].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: __('Embassy Management'),
    single_column: true
  });

  const cards = [
    {
      label: __('Consular Applications'),
      description: __('Review submitted, draft, urgent, and completed cases.'),
      action: () => frappe.set_route('List', 'Consular Application')
    },
    {
      label: __('Officer Workbench'),
      description: __('Open the officer queue for review and case actions.'),
      action: () => frappe.set_route('officer-workbench')
    },
    {
      label: __('Appointments'),
      description: __('Manage bookings, slots, walk-ins, and no-shows.'),
      action: () => frappe.set_route('List', 'Embassy Appointment')
    },
    {
      label: __('Consular Services'),
      description: __('Configure visas, passports, cards, attestations, fees, and requirements.'),
      action: () => frappe.set_route('List', 'Consular Service')
    },
    {
      label: __('Finance Dashboard'),
      description: __('Track payment reviews, revenue, and pending confirmations.'),
      action: () => frappe.set_route('embassy-finance-dashboard')
    },
    {
      label: __('Applicant Portal'),
      description: __('Open the public embassy portal in a new tab.'),
      action: () => window.open('/embassy', '_blank', 'noopener')
    }
  ];

  const body = $(`
    <div class="ems-home">
      <section class="ems-home-hero">
        <img class="ems-home-icon" src="/assets/embassy_management/img/app_icon.svg" alt="EMS">
        <div>
          <div class="ems-home-kicker">${__('Embassy Management ERPNext')}</div>
          <h2>${__('Configurable consular operations for any diplomatic mission.')}</h2>
          <p>${__('Manage online applications, appointments, documents, payments, officer review, and reporting from one upgrade-safe ERPNext app.')}</p>
        </div>
      </section>
      <section class="ems-home-grid">
        ${cards.map((card, index) => `
          <button class="ems-home-card" type="button" data-index="${index}">
            <strong>${frappe.utils.escape_html(card.label)}</strong>
            <span>${frappe.utils.escape_html(card.description)}</span>
          </button>
        `).join('')}
      </section>
      <div class="ems-home-footer">
        <a href="https://viewertech.net" target="_blank" rel="noopener">Powered by Viewertech</a>
      </div>
    </div>
  `).appendTo(page.body);

  body.find('.ems-home-card').on('click', function () {
    cards[Number($(this).data('index'))].action();
  });
};
