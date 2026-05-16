frappe.ready(function () {
  const servicesRoot = document.querySelector('#ems-services');
  if (servicesRoot) {
    frappe.call({
      method: 'embassy_management.api.portal.get_public_services',
      callback: function (response) {
        const services = response.message || [];
        servicesRoot.innerHTML = services.map(service => `
          <article class="ems-card">
            <h3>${frappe.utils.escape_html(service.service_name || service.name)}</h3>
            <p>${frappe.utils.escape_html(service.description || '')}</p>
            <p><strong>${frappe.utils.escape_html(service.default_processing_time || '')}</strong></p>
            <a class="btn btn-sm btn-primary" href="/embassy/apply?service=${encodeURIComponent(service.name)}">${__('Apply')}</a>
          </article>
        `).join('');
      }
    });
  }

  const appRoot = document.querySelector('#ems-root');
  const shell = document.querySelector('[data-ems-page]');
  if (appRoot && shell) {
    const page = shell.dataset.emsPage;
    if (page === 'requirements') {
      appRoot.innerHTML = `
        <form class="ems-requirements-form">
          <div class="form-group"><label>${__('Service')}</label><select class="form-control" name="service"></select></div>
          <div class="form-group"><label>${__('Nationality')}</label><input class="form-control" name="nationality"></div>
          <div class="form-group"><label>${__('Residence Country')}</label><input class="form-control" name="residence_country"></div>
          <button class="btn btn-primary" type="submit">${__('Check')}</button>
          <div class="ems-results mt-4"></div>
        </form>`;
      loadServicesForSelect(appRoot.querySelector('select[name="service"]'));
    } else if (page === 'dashboard') {
      appRoot.innerHTML = `<button class="btn btn-primary" id="ems-load-dashboard">${__('Load My Dashboard')}</button><div class="ems-results mt-4"></div>`;
    } else {
      appRoot.innerHTML = `
        <div class="ems-upload">
          <div>
            <h3>${__('Start a secure online application')}</h3>
            <p>${__('Select a service, save drafts, upload documents, book appointments, and review before final submission.')}</p>
            <button class="btn btn-primary" id="ems-start-application">${__('Start Application')}</button>
          </div>
        </div>`;
    }
  }
});

function loadServicesForSelect(select) {
  frappe.call({
    method: 'embassy_management.api.portal.get_public_services',
    callback: function (response) {
      const services = response.message || [];
      select.innerHTML = services.map(service => `<option value="${frappe.utils.escape_html(service.name)}">${frappe.utils.escape_html(service.service_name)}</option>`).join('');
    }
  });
}
