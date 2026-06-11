frappe.ready(function () {
  const servicesRoot = document.querySelector('#ems-services');
  if (servicesRoot) {
    servicesRoot.innerHTML = `<div class="ems-empty">${__('Loading services...')}</div>`;
    frappe.call({
      method: 'embassy_management.api.portal.get_public_services',
      callback: function (response) {
        const services = response.message || [];
        servicesRoot.innerHTML = services.length ? services.map(renderServiceCard).join('') : `<div class="ems-empty">${__('No public services are currently enabled.')}</div>`;
      },
      error: function () {
        servicesRoot.innerHTML = `<div class="ems-empty">${__('Services could not be loaded.')}</div>`;
      }
    });
  }

  const appRoot = document.querySelector('#ems-root');
  const shell = document.querySelector('[data-ems-page]');
  if (!appRoot || !shell) {
    return;
  }

  const page = shell.dataset.emsPage;
  if (page === 'requirements') {
    renderRequirements(appRoot);
  } else if (page === 'dashboard') {
    renderDashboard(appRoot);
  } else {
    renderApplicationStart(appRoot);
  }
});

function emsEscape(value) {
  return frappe.utils.escape_html(value == null ? '' : String(value));
}

function renderServiceCard(service) {
  const fee = service.default_fee ? `${emsEscape(service.currency || '')} ${emsEscape(service.default_fee)}` : __('Configured by mission');
  return `
    <article class="ems-card">
      <div>
        <span class="ems-chip">${emsEscape(service.service_category || __('Service'))}</span>
      </div>
      <h3>${emsEscape(service.service_name || service.name)}</h3>
      <p>${emsEscape(service.description || __('Consular service'))}</p>
      <div class="ems-card-meta">
        <span class="ems-chip">${emsEscape(service.default_processing_time || __('Processing time varies'))}</span>
        <span class="ems-chip">${fee}</span>
      </div>
      <div class="ems-actions">
        <a class="btn btn-sm btn-primary" href="/embassy/apply?service=${encodeURIComponent(service.name)}">${__('Apply')}</a>
        <a class="btn btn-sm btn-outline-primary" href="/embassy/requirements?service=${encodeURIComponent(service.name)}">${__('Requirements')}</a>
      </div>
    </article>
  `;
}

function renderRequirements(appRoot) {
  appRoot.innerHTML = `
    <form class="ems-requirements-form">
      <div class="ems-form-grid">
        <div class="form-group">
          <label>${__('Service')}</label>
          <select class="form-control" name="service" required></select>
        </div>
        <div class="form-group">
          <label>${__('Nationality')}</label>
          <input class="form-control" name="nationality" autocomplete="country-name">
        </div>
        <div class="form-group">
          <label>${__('Residence Country')}</label>
          <input class="form-control" name="residence_country" autocomplete="country-name">
        </div>
      </div>
      <button class="btn btn-primary" type="submit">${__('Check Requirements')}</button>
      <div class="ems-results"></div>
    </form>`;

  const select = appRoot.querySelector('select[name="service"]');
  loadServicesForSelect(select, new URLSearchParams(window.location.search).get('service'));

  appRoot.querySelector('form').addEventListener('submit', function (event) {
    event.preventDefault();
    const results = appRoot.querySelector('.ems-results');
    results.innerHTML = `<div class="ems-empty">${__('Checking requirements...')}</div>`;
    frappe.call({
      method: 'embassy_management.api.requirements.evaluate_requirements',
      args: {
        service: select.value,
        nationality: appRoot.querySelector('[name="nationality"]').value,
        residence_country: appRoot.querySelector('[name="residence_country"]').value
      },
      callback: function (response) {
        results.innerHTML = renderRequirementResult(response.message || {});
      },
      error: function () {
        results.innerHTML = `<div class="ems-empty">${__('Requirements could not be checked.')}</div>`;
      }
    });
  });
}

function renderRequirementResult(data) {
  const documents = data.required_documents || [];
  const notices = data.notices || [];
  return `
    <div class="ems-panel-grid">
      <article class="ems-card">
        <span class="ems-chip">${emsEscape(data.eligibility || __('Eligibility'))}</span>
        <h3>${emsEscape(data.service_name || __('Selected service'))}</h3>
        <p>${emsEscape(data.instructions || __('Follow the mission instructions shown for this service.'))}</p>
        <div class="ems-card-meta">
          <span class="ems-chip">${emsEscape(data.currency || '')} ${emsEscape(data.fee || 0)}</span>
          <span class="ems-chip">${emsEscape(data.processing_time || __('Processing time varies'))}</span>
          <span class="ems-chip">${data.requires_appointment ? __('Appointment required') : __('No appointment required')}</span>
        </div>
      </article>
      <article class="ems-card">
        <h3>${__('Required Documents')}</h3>
        <div class="ems-result-list">
          ${documents.length ? documents.map(doc => `
            <div class="ems-result-row">
              <strong>${emsEscape(doc.requirement_label || doc.document_category)}</strong>
              <p>${emsEscape(doc.instructions || '')}</p>
              <span class="ems-chip">${doc.mandatory ? __('Mandatory') : __('Optional')}</span>
            </div>
          `).join('') : `<div class="ems-empty">${__('No documents configured.')}</div>`}
        </div>
      </article>
    </div>
    ${notices.length ? `
      <div class="ems-results">
        ${notices.map(notice => `
          <div class="ems-result-row">
            <strong>${emsEscape(notice.title || __('Notice'))}</strong>
            <p>${emsEscape(notice.message || '')}</p>
          </div>
        `).join('')}
      </div>
    ` : ''}
  `;
}

function renderDashboard(appRoot) {
  appRoot.innerHTML = `<div class="ems-empty">${__('Loading dashboard...')}</div>`;
  frappe.call({
    method: 'embassy_management.api.portal.applicant_dashboard',
    callback: function (response) {
      const data = response.message || {};
      const applications = data.applications || [];
      const appointments = data.appointments || [];
      const stripeEnabled = Boolean(data.stripe_enabled);
      const canPayWithStripe = (app) => {
        const inactiveStatuses = ['Draft', 'Rejected', 'Cancelled', 'Completed', 'Collected / Dispatched'];
        const closedPaymentStatuses = ['Not Required', 'Payment Confirmed', 'Refunded'];
        return stripeEnabled
          && Number(app.total_fee || 0) > 0
          && !inactiveStatuses.includes(app.application_status)
          && !closedPaymentStatuses.includes(app.payment_status);
      };
      appRoot.innerHTML = `
        <div class="ems-portal-actions">
          <a class="btn btn-primary" href="/embassy/apply" title="${__('Start a new online consular application')}">${__('Start Application')}</a>
          <a class="btn btn-outline-primary" href="/embassy/requirements" title="${__('Check service eligibility, fees, and document requirements')}">${__('Check Requirements')}</a>
        </div>
        <div class="ems-panel-grid">
          <article class="ems-card">
            <span class="ems-chip">${__('Applications')}</span>
            <h3>${applications.length}</h3>
            <p>${__('Submitted and draft consular applications.')}</p>
          </article>
          <article class="ems-card">
            <span class="ems-chip">${__('Appointments')}</span>
            <h3>${appointments.length}</h3>
            <p>${__('Booked consular appointments.')}</p>
          </article>
        </div>
        <div class="ems-results ems-panel-grid">
          <article class="ems-card">
            <h3>${__('My Applications')}</h3>
            <div class="ems-result-list">
              ${applications.length ? applications.map(app => `
                <div class="ems-result-row">
                  <strong>${emsEscape(app.application_number || app.name)}</strong>
                  <p>${emsEscape(app.service_label || app.service || '')} - ${emsEscape(app.application_status || '')}</p>
                  <span class="ems-chip">${emsEscape(app.payment_status || __('Payment status not set'))}</span>
                  ${canPayWithStripe(app) ? `
                    <div class="ems-actions">
                      <button class="btn btn-primary btn-sm" type="button" data-stripe-pay="${emsEscape(app.name)}" title="${__('Pay securely using Stripe Checkout')}">${__('Pay with Stripe')}</button>
                    </div>
                  ` : ''}
                </div>
              `).join('') : `
                <div class="ems-empty">
                  <div>
                    <strong>${__('No applications yet')}</strong>
                    <div class="ems-actions">
                      <a class="btn btn-primary btn-sm" href="/embassy/apply">${__('Start Application')}</a>
                    </div>
                  </div>
                </div>
              `}
            </div>
          </article>
          <article class="ems-card">
            <h3>${__('Appointments')}</h3>
            <div class="ems-result-list">
              ${appointments.length ? appointments.map(item => `
                <div class="ems-result-row">
                  <strong>${emsEscape(item.booking_code || __('Appointment'))}</strong>
                  <p>${emsEscape(item.service_label || item.service || '')} - ${emsEscape(item.appointment_date || '')} ${emsEscape(item.start_time || '')}</p>
                  <span class="ems-chip">${emsEscape(item.status || '')}</span>
                </div>
              `).join('') : `<div class="ems-empty">${__('No appointments booked.')}</div>`}
            </div>
          </article>
        </div>
      `;
      appRoot.querySelectorAll('[data-stripe-pay]').forEach(button => {
        button.addEventListener('click', function () {
          const application = this.getAttribute('data-stripe-pay');
          this.disabled = true;
          this.textContent = __('Opening Stripe...');
          frappe.call({
            method: 'embassy_management.api.stripe_payments.create_checkout_session',
            args: { application },
            callback: function (payResponse) {
              const payload = payResponse.message || {};
              if (payload.checkout_url) {
                window.location.href = payload.checkout_url;
              }
            },
            error: () => {
              this.disabled = false;
              this.textContent = __('Pay with Stripe');
            }
          });
        });
      });
    },
    error: function () {
      appRoot.innerHTML = `<div class="ems-empty">${__('Please log in to view the applicant dashboard.')}</div>`;
    }
  });
}

function renderApplicationStart(appRoot) {
  appRoot.innerHTML = `
    <div class="ems-upload">
      <div>
        <h3>${__('Start a secure online application')}</h3>
        <p>${__('Choose a public service, save a draft, upload supporting documents, and submit the declaration when ready.')}</p>
        <div class="ems-actions">
          <select class="form-control" name="service" aria-label="${__('Service')}"></select>
          <button class="btn btn-primary" id="ems-start-application" type="button">${__('Start Application')}</button>
        </div>
      </div>
    </div>
    <div class="ems-results"></div>`;

  const select = appRoot.querySelector('select[name="service"]');
  loadServicesForSelect(select, new URLSearchParams(window.location.search).get('service'));

  appRoot.querySelector('#ems-start-application').addEventListener('click', function () {
    const results = appRoot.querySelector('.ems-results');
    if (!select.value) {
      results.innerHTML = `<div class="ems-empty">${__('Select a service first.')}</div>`;
      return;
    }
    results.innerHTML = `<div class="ems-empty">${__('Creating draft application...')}</div>`;
    frappe.call({
      method: 'embassy_management.api.portal.create_application',
      args: { service: select.value },
      callback: function (response) {
        const doc = response.message || {};
        results.innerHTML = `
          <div class="ems-result-row">
            <strong>${__('Draft application created')}</strong>
            <p>${emsEscape(doc.application_number || doc.name)}</p>
            <a class="btn btn-primary btn-sm" href="/embassy/dashboard">${__('Open Dashboard')}</a>
          </div>`;
      },
      error: function () {
        results.innerHTML = `<div class="ems-empty">${__('Log in before starting an application.')}</div>`;
      }
    });
  });
}

function loadServicesForSelect(select, selected) {
  frappe.call({
    method: 'embassy_management.api.portal.get_public_services',
    callback: function (response) {
      const services = response.message || [];
      select.innerHTML = `<option value="">${__('Select a service')}</option>` + services.map(service => `<option value="${emsEscape(service.name)}">${emsEscape(service.service_name || service.name)}</option>`).join('');
      if (selected) {
        select.value = selected;
      }
    },
    error: function () {
      select.innerHTML = `<option value="">${__('Services unavailable')}</option>`;
    }
  });
}
