# Copyright (c) 2022, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint, scrub
from frappe.model.document import Document
from erpnext.accounts.party import get_party_account
from erpnext.accounts.utils import get_account_currency
from frappe.utils import flt,nowdate,cstr
from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry
from erpnext.accounts.doctype.bank_account.bank_account import (
	get_bank_account_details,
	get_party_bank_account,
)
from frappe.utils import nowdate,get_link_to_form
from frappe.utils.data import getdate, nowdate
from erpnext.non_profit.doctype.member.member import create_customer


class MaintenanceTicketCD(Document):
	def before_insert(self):
		if  self.customer_type=='Outside':
			customer = create_customer(
				frappe._dict({"fullname": self.customer_for_outside, "email": None, "phone": self.phone_no or None})
			)
			self.customer = customer
			msg=_("Customer {0} is created".format(frappe.bold(get_link_to_form("Customer Entry",customer))))	
			frappe.msgprint(msg=msg,title="Customer is created.",indicator="green")			

	def validate(self):
		self.advance_amount=get_advance_amount_from_payment_entry(self.name)
		self.create_stock_entry_for_material_issue()

	def create_stock_entry_for_material_issue(self):
		default_expense_account=frappe.get_cached_value("Company",self.company, "default_expense_account")
		cost_center = frappe.get_cached_value("Company",self.company, "cost_center")
		stock_entry = frappe.new_doc("Stock Entry")
		stock_entry.purpose = "Material Issue"
		stock_entry.set_stock_entry_type()
		stock_entry.company = self.company
		consumed_se_items=[]
		consumed_se_items_hex_name=[]
		for consumed in self.maintenance_ticket_consumed_material or []:
			if consumed.stock_entry==None:
				se_child = stock_entry.append("items")
				se_child.item_code = consumed.item
				se_child.item_name = frappe.db.get_value("Item", consumed.item, "item_name")
				se_child.uom = frappe.db.get_value("Item", consumed.item, "stock_uom")
				se_child.stock_uom =  frappe.db.get_value("Item", consumed.item, "stock_uom")
				se_child.qty = flt(consumed.qty)
				se_child.conversion_factor = 1
				se_child.cost_center = cost_center
				se_child.expense_account = default_expense_account
				se_child.s_warehouse=consumed.warehouse
				se_child.serial_no=consumed.serial_no or None
				consumed_se_items.append(cstr(consumed.idx)+"::"+consumed.item)
				consumed_se_items_hex_name.append(consumed.name)
		if len(consumed_se_items)>0:
			consumed_se_items_str=", ".join(consumed_se_items)
			stock_entry.remarks = _(" It is created from maintenance ticket {0} and items {1}").format(self.name,", ".join(consumed_se_items))
			stock_entry.save(ignore_permissions=True)		
			print('consumed_se_items',consumed_se_items)
			msg=_("Material Issue {0} is created based on maintenance ticket {1} and consumed items {2}"
				.format(frappe.bold(get_link_to_form("Stock Entry",stock_entry.name)),frappe.bold(consumed.item),consumed_se_items_str))	
			frappe.msgprint(msg=msg,title="Stock Entry is created.",indicator="green")
			for consumed in self.maintenance_ticket_consumed_material or []:
				if consumed.name in consumed_se_items_hex_name:
					consumed.stock_entry=stock_entry.name



	@frappe.whitelist()
	def create_sales_invoice(self):
		# 	1st year			shipping_amount
		# 	2nd year			shipping_amount +  consumed
		# outside	> 2nd year			shipping_amount +  consumed + maintenance amount		
		si = frappe.new_doc('Sales Invoice')
		si.customer=self.customer
		si.due_date=getdate(nowdate())
		si.cost_center=frappe.db.get_value('Company', self.company, 'cost_center')
		# shipping
		if self.shipping_amount>0:
			default_shipping_item_cf = frappe.db.get_value('Company', self.company, 'default_shipping_item_cf')
			row = si.append('items', {})		
			row.item_code=default_shipping_item_cf
			row.item_name=frappe.db.get_value("Item",row.item_code, "item_name")
			row.qty=1
			row.rate=self.shipping_amount	
		# maintenance amount
		if self.warranty_status=='Not Applicable' and self.maintenance_amount>0:
			maintenance_item = frappe.db.get_value('Maintenance Type', self.maintenance_type, 'item')
			row = si.append('items', {})		
			row.item_code=maintenance_item
			row.item_name=frappe.db.get_value("Item",row.item_code, "item_name")
			row.qty=1
			row.rate=self.maintenance_amount
		# cosumed material
		if self.customer_type=='Outside' or (self.customer_type=='Existing' and self.warranty_status!='1st Year'):
			for item in self.maintenance_ticket_consumed_material or []:
				row = si.append('items', {})		
				row.item_code=item.item
				row.item_name=frappe.db.get_value("Item",row.item_code, "item_name")
				row.qty=item.qty
				# row.rate=item.price
		si.flags.ignore_permissions = True
		si.maintenance_ticket_cf=self.name
		si.run_method("set_missing_values")
		si.run_method("calculate_taxes_and_totals")		
		si.save()		
		msg = _('Sales Invoice {} is created'.format(frappe.bold(get_link_to_form('Sales Invoice',si.name))))
		frappe.msgprint(msg)					

	@frappe.whitelist()
	def get_shipping_amount(self):
		if self.company:
			default_shipping_item_cf = frappe.db.get_value('Company', self.company, 'default_shipping_item_cf')
			if default_shipping_item_cf:
				shipping_amount= frappe.db.sql(
					"""SELECT item_price.price_list_rate  FROM `tabItem` as item inner join `tabItem Price` item_price 
					on item.item_code =item_price.item_code  and item_price.selling =1 
					where item.item_code=  %(item)s limit 1
					""",{ "item": default_shipping_item_cf},as_dict=1,debug=1)
				if len(shipping_amount)>0:
					self.shipping_amount=shipping_amount[0].get('price_list_rate')
					return self.shipping_amount


def get_advance_amount_from_payment_entry(maintenance_ticket_cf):
	paid_amount= frappe.db.sql(
		"""SELECT sum(paid_amount) as total_paid_amount FROM `tabPayment Entry` 
		where maintenance_ticket_cf=  %(maintenance_ticket_cf)s 
		and docstatus=1
		group by maintenance_ticket_cf
		""",{ "maintenance_ticket_cf": maintenance_ticket_cf},as_dict=1,debug=1)
	if len(paid_amount)>0:
		advance_amount=paid_amount[0].get('total_paid_amount')
		return advance_amount

@frappe.whitelist()
def get_payment_entry_against_maintenance_ticket(dt, dn):
	reference_doc = None
	doc = frappe.get_doc(dt, dn)
	party_type = "Customer"
	party_account = get_party_account(party_type, doc.get(party_type.lower()), doc.company)
	party_account_currency = doc.get("party_account_currency") or get_account_currency(party_account)
	payment_type = "Receive"
	# paid_amount=doc.maintenance_amount
	pe = frappe.new_doc("Payment Entry")
	pe.maintenance_ticket_cf=doc.name
	pe.payment_type = payment_type
	pe.company = doc.company
	# pe.cost_center = doc.get("cost_center")
	pe.posting_date = nowdate()
	# pe.mode_of_payment = doc.get("mode_of_payment")
	pe.party_type = party_type
	pe.party = doc.get(scrub(party_type))
	# pe.contact_person = doc.get("contact_person")
	# pe.contact_email = doc.get("contact_email")
	pe.paid_from = party_account 
	pe.paid_from_account_currency = party_account_currency
	# pe.paid_amount = paid_amount
	# pe.received_amount = received_amount
	bank_account = get_party_bank_account(pe.party_type, pe.party)
	pe.set("bank_account", bank_account)
	pe.set_bank_account_data()
	pe.setup_party_account_field()
	pe.set_missing_values()
	return pe


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_items_of_customer(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("customer"):
		frappe.msgprint(_("Please select a Customer first."))
		return []

	return frappe.db.sql(
		"""SELECT item_code,item_name FROM `tabSerial No` where customer =%(customer)s and status='Delivered'
		GROUP BY item_code 
		limit {start}, {page_len}""".format(doctype,start=start, page_len=page_len
		),
		{"txt": "%{0}%".format(txt), "_txt": txt.replace("%", ""), "customer": filters["customer"]},
	)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_serial_nos_of_customer(doctype, txt, searchfield, start, page_len, filters):
	if not filters.get("customer"):
		frappe.msgprint(_("Please select a Customer first."))
		return []

	if not filters.get("item"):
		frappe.msgprint(_("Please select a Item first."))
		return []

	return frappe.db.sql(
		"""SELECT serial_no,item_code  FROM `tabSerial No` where item_code = %(item)s and customer = %(customer)s and status='Delivered'
		limit {start}, {page_len}""".format(doctype,start=start, page_len=page_len),
		{"txt": "%{0}%".format(txt), "_txt": txt.replace("%", ""), "item": filters["item"],"customer": filters["customer"]},debug=1
	)	

@frappe.whitelist()
def remove_maintenance_ticket_reference_from_sales_invoice(self,method):	
	if self.maintenance_ticket_cf:
		maintenance_status= frappe.db.get_value('Maintenance Ticket CD', self.maintenance_ticket_cf, 'status')
		if maintenance_status=='Billed':
			frappe.db.set_value('Maintenance Ticket CD', self.maintenance_ticket_cf, 'status','Under Process')
			msg = _('Maintenance Ticket {0} status is changed <b>Under Process</b>'.format(self.maintenance_ticket_cf))
			frappe.msgprint(msg=msg,alert=1)		

		frappe.db.set_value('Sales Invoice',self.name, 'maintenance_ticket_cf', None)
		msg = _('Maintenance Ticket {0} reference is removed from Sales Invoice {1}'.format(self.maintenance_ticket_cf,self.name))
		frappe.msgprint(msg=msg,alert=1)
			
@frappe.whitelist()
def remove_maintenance_ticket_reference_from_payment_entry(self,method):
	if self.maintenance_ticket_cf :	
		frappe.db.set_value('Payment Entry',self.name, 'maintenance_ticket_cf', None)
		msg = _('Maintenance Ticket {0} reference is removed from Payment Entry {1}'.format(self.maintenance_ticket_cf,self.name))
		frappe.msgprint(msg=msg,alert=1)
		update_maintenance_ticket_advance_amount_from_payment_entry(self,method)

@frappe.whitelist()
def update_maintenance_ticket_advance_amount_from_payment_entry(self,method):
	if self.maintenance_ticket_cf :
		advance_amount=get_advance_amount_from_payment_entry(self.maintenance_ticket_cf) or 0
		frappe.db.set_value('Maintenance Ticket CD', self.maintenance_ticket_cf, 'advance_amount',flt(advance_amount))
		msg = _('Maintenance Ticket {0} advance amount is updated to <b>{1}</b>'.format(self.maintenance_ticket_cf,advance_amount))
		frappe.msgprint(msg=msg,alert=1)		

@frappe.whitelist()
def remove_stock_entry_reference_from_maintenance_ticket(self,method):	
	ticket_list=frappe.db.get_list('Maintenance Ticket Consumed Material', filters={'stock_entry': ['=', self.name]},fields=['name','parent'],as_dict=1)	
	for ticket in ticket_list or []:
		if ticket.name:
			frappe.db.set_value('Maintenance Ticket Consumed Material', ticket.name, 'stock_entry', None)
			msg = _('Stock Entry reference are removed from consumed material table for Maintenance Ticket {0}'.format(ticket.parent))
			frappe.msgprint(msg=msg,alert=1)			