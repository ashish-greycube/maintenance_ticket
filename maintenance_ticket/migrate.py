import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_migrate():
    custom_fields = {
        "Company": [
            {
				"fieldname":'default_shipping_item_cf',
				"fieldtype":'Link',
                "label":'Default Shipping Item',
                "options":'Item',
				"insert_after":'default_holiday_list',
				"is_custom_field":1,
				"is_system_generated":0,
            }		
        ],
    }
    print("Creating Custom Fields in Code Doctypes.....")
    for dt, fields in custom_fields.items():
        print("*******\n %s: " % dt, [d.get("fieldname") for d in fields])
    create_custom_fields(custom_fields)