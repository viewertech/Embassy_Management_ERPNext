frappe.ui.form.on('Consular Application', {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Create Sales Invoice'), () => {
                frappe.call({
                    method: 'embassy_management.api.finance.create_sales_invoice',
                    args: { application: frm.doc.name },
                    callback: () => frm.reload_doc()
                });
            }, __('Finance'));
        }
    }
});
