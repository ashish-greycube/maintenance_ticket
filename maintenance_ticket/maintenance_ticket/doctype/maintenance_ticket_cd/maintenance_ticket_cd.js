// Copyright (c) 2022, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Maintenance Ticket CD', {
	refresh: function (frm) {
		if (frm.is_new() === undefined && frm.doc.status.includes('Closed', 'Billed') == false) {
			frm.add_custom_button(__("Payment"), function () {
				frm.events.make_payment_entry(frm);
			}, __('Create'));
			frm.add_custom_button(__("Invoice"), function () {
				frm.events.make_invoice_entry(frm);
			}, __('Create'));
			frm.page.set_inner_btn_group_as_primary(__('Create'));

		}
	},
	item_sold_date: function (frm) {
		if (frm.doc.item_sold_date && frm.doc.ticket_date) {
			let no_of_days_since_sold = frappe.datetime.get_diff(frm.doc.ticket_date, frm.doc.item_sold_date)
			if (no_of_days_since_sold <= 365) {
				frm.set_value('warranty_status', '1st Year')
			} else if (no_of_days_since_sold > 365 && no_of_days_since_sold <= 730) {
				frm.set_value('warranty_status', '2nd Year')
			} else {
				frm.set_value('warranty_status', 'Not Applicable')
			}
		}
	},
	make_invoice_entry: function (frm) {
		if (frm.doc.maintenance_type==undefined || frm.doc.maintenance_type=='') {
			frappe.throw(__('Please select Maintenance Type to proceed..'))
		}
		frappe.call({
			method: "create_sales_invoice",
			doc: frm.doc,
			callback: function (r) {
				if (!r.exc) {
					console.log(r)
					// frm.refresh_fields('function_sheet_extra_item')
				}
			}
		});
	},
	make_payment_entry: function (frm) {
		return frappe.call({
			method: "maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.get_payment_entry_against_maintenance_ticket",
			args: {
				"dt": cur_frm.doc.doctype,
				"dn": cur_frm.doc.name
			},
			callback: function (r) {
				var doclist = frappe.model.sync(r.message);
				frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
				// cur_frm.refresh_fields()
			}
		});
	},
	onload: function (frm) {
		get_serial_nos_of_customer(frm)
		get_items_of_customer(frm)
		frm.set_query('item', 'maintenance_ticket_consumed_material', () => {
			return {
				filters: {
					disabled: 0,
					is_stock_item: 1
				}
			}
		})
		frm.set_query('serial_no', 'maintenance_ticket_consumed_material', (doc, cdt, cdn) => {
			var row = locals[cdt][cdn];
			return {
				filters: {
					item_code: row.item,
				}
			}
		})
	},
	include_shipping_service: function (frm) {
		if (frm.doc.include_shipping_service == 1) {
			frm.call('get_shipping_amount')
				.then(r => {
					console.log(r)
					if (r.message) {
						frm.refresh_field('shipping_amount')
					}
				})
		}
	}
});

function get_serial_nos_of_customer(frm) {
	frm.set_query('serial_no', () => {
		if (frm.doc.customer && frm.doc.customer_type == 'Existing' && frm.doc.item) {
			return {
				query: 'maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.get_serial_nos_of_customer',
				filters: {
					customer: frm.doc.customer,
					item: frm.doc.item
				}
			}
		}
	})
}

function get_items_of_customer(frm) {
	frm.set_query('item', () => {
		if (frm.doc.customer && frm.doc.customer_type == 'Existing') {
			return {
				query: 'maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.get_items_of_customer',
				filters: {
					customer: frm.doc.customer
				}
			}
		}
	})
}