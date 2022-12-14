from . import __version__ as app_version

app_name = "maintenance_ticket"
app_title = "Maintenance Ticket"
app_publisher = "GreyCube Technologies"
app_description = "customization for asante maintenance ticket"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "admin@greycube.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/maintenance_ticket/css/maintenance_ticket.css"
# app_include_js = "/assets/maintenance_ticket/js/maintenance_ticket.js"

# include js, css files in header of web template
# web_include_css = "/assets/maintenance_ticket/css/maintenance_ticket.css"
# web_include_js = "/assets/maintenance_ticket/js/maintenance_ticket.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "maintenance_ticket/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "maintenance_ticket.install.before_install"
# after_install = "maintenance_ticket.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "maintenance_ticket.uninstall.before_uninstall"
# after_uninstall = "maintenance_ticket.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "maintenance_ticket.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Sales Invoice": 
	{"on_cancel": 
	"maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.remove_maintenance_ticket_reference_from_sales_invoice",
	"on_trash":
	"maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.remove_maintenance_ticket_reference_from_sales_invoice"
	},
	"Payment Entry": 
	{"on_cancel": 
	"maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.remove_maintenance_ticket_reference_from_payment_entry",
	"on_submit":
	"maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.update_maintenance_ticket_advance_amount_from_payment_entry",
	"on_trash":
	"maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.remove_maintenance_ticket_reference_from_payment_entry"
	},
	"Stock Entry":{
		"on_cancel":
		"maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.remove_stock_entry_reference_from_maintenance_ticket",
		"on_trash":
		"maintenance_ticket.maintenance_ticket.doctype.maintenance_ticket_cd.maintenance_ticket_cd.remove_stock_entry_reference_from_maintenance_ticket"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"maintenance_ticket.tasks.all"
#	],
#	"daily": [
#		"maintenance_ticket.tasks.daily"
#	],
#	"hourly": [
#		"maintenance_ticket.tasks.hourly"
#	],
#	"weekly": [
#		"maintenance_ticket.tasks.weekly"
#	]
#	"monthly": [
#		"maintenance_ticket.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "maintenance_ticket.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "maintenance_ticket.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "maintenance_ticket.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"maintenance_ticket.auth.validate"
# ]

