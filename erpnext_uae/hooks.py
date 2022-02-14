from . import __version__ as app_version

app_name = "erpnext_uae"
app_title = "ERPNext UAE"
app_publisher = "Frappe Technologies Private Limited"
app_description = "Frappe app tbuilt on top of ERPNext to hold regional settings for Unitedd Arab Emirates"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "diksha@frappe.io"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_uae/css/erpnext_uae.css"
# app_include_js = "/assets/erpnext_uae/js/erpnext_uae.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_uae/css/erpnext_uae.css"
# web_include_js = "/assets/erpnext_uae/js/erpnext_uae.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_uae/public/scss/website"

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

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpnext_uae.utils.jinja_methods",
# 	"filters": "erpnext_uae.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpnext_uae.install.before_install"
after_install = "erpnext_uae.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "erpnext_uae.uninstall.before_uninstall"
# after_uninstall = "erpnext_uae.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_uae.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Purchase Invoice": {
		"validate": [
			"erpnext_uae.utils.validate_reverse_charge_transaction",
			"erpnext_uae.utils.update_itc_availed_fields",
			"erpnext_uae.utils.update_grand_total_for_rcm",
			"erpnext_uae.utils.validate_returns",
			"erpnext_uae.utils.update_taxable_values"
		]
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"erpnext_uae.tasks.all"
# 	],
# 	"daily": [
# 		"erpnext_uae.tasks.daily"
# 	],
# 	"hourly": [
# 		"erpnext_uae.tasks.hourly"
# 	],
# 	"weekly": [
# 		"erpnext_uae.tasks.weekly"
# 	],
# 	"monthly": [
# 		"erpnext_uae.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "erpnext_uae.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_uae.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_uae.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpnext_uae.auth.validate"
# ]

regional_overrides = {
	'United Arab Emirates': {
		'erpnext.controllers.taxes_and_totals.update_itemised_tax_data': 'erpnext_uae.utils.update_itemised_tax_data',
		'erpnext.accounts.doctype.purchase_invoice.purchase_invoice.make_regional_gl_entries': 'erpnext_uae.utils.make_regional_gl_entries',
	},
}