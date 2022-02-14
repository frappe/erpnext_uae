import frappe
from frappe import _
from frappe.utils import cint, flt, money_in_words, round_based_on_smallest_currency_fraction
import erpnext
from erpnext.controllers.taxes_and_totals import get_itemised_tax


def update_itemised_tax_data(doc):
	if not doc.taxes: return

	itemised_tax = get_itemised_tax(doc.taxes)

	for row in doc.items:
		tax_rate = 0.0
		item_tax_rate = 0.0

		if row.item_tax_rate:
			item_tax_rate = frappe.parse_json(row.item_tax_rate)

		# First check if tax rate is present
		# If not then look up in item_wise_tax_detail
		if item_tax_rate:
			for account, rate in item_tax_rate.items():
				tax_rate += rate
		elif row.item_code and itemised_tax.get(row.item_code):
			tax_rate = sum([tax.get('tax_rate', 0) for d, tax in itemised_tax.get(row.item_code).items()])

		row.tax_rate = flt(tax_rate, row.precision("tax_rate"))
		row.tax_amount = flt((row.net_amount * tax_rate) / 100, row.precision("net_amount"))
		row.total_amount = flt((row.net_amount + row.tax_amount), row.precision("total_amount"))

def get_account_currency(account):
	"""Helper function to get account currency."""
	if not account:
		return
	def generator():
		account_currency, company = frappe.get_cached_value(
			"Account",
			account,
			["account_currency",
			"company"]
		)
		if not account_currency:
			account_currency = frappe.get_cached_value('Company',  company,  "default_currency")

		return account_currency

	return frappe.local_cache("account_currency", account, generator)

def get_tax_accounts(company):
	"""Get the list of tax accounts for a specific company."""
	tax_accounts_dict = frappe._dict()
	tax_accounts_list = frappe.get_all("UAE VAT Account",
		filters={"parent": company},
		fields=["Account"]
		)

	if not tax_accounts_list and not frappe.flags.in_test:
		frappe.throw(_('Please set Vat Accounts for Company: "{0}" in UAE VAT Settings').format(company))
	for tax_account in tax_accounts_list:
		for account, name in tax_account.items():
			tax_accounts_dict[name] = name

	return tax_accounts_dict

def update_grand_total_for_rcm(doc, method):
	"""If the Reverse Charge is Applicable subtract the tax amount from the grand total and update in the form."""
	country = frappe.get_cached_value('Company', doc.company, 'country')

	if country != 'United Arab Emirates':
		return

	if not doc.total_taxes_and_charges:
		return

	if doc.reverse_charge == 'Y':
		tax_accounts = get_tax_accounts(doc.company)

		base_vat_tax = 0
		vat_tax = 0

		for tax in doc.get('taxes'):
			if tax.category not in ("Total", "Valuation and Total"):
				continue

			if flt(tax.base_tax_amount_after_discount_amount) and tax.account_head in tax_accounts:
				base_vat_tax += tax.base_tax_amount_after_discount_amount
				vat_tax += tax.tax_amount_after_discount_amount

		doc.taxes_and_charges_added -= vat_tax
		doc.total_taxes_and_charges -= vat_tax
		doc.base_taxes_and_charges_added -= base_vat_tax
		doc.base_total_taxes_and_charges -= base_vat_tax

		update_totals(vat_tax, base_vat_tax, doc)

def update_totals(vat_tax, base_vat_tax, doc):
	"""Update the grand total values in the form."""
	doc.base_grand_total -= base_vat_tax
	doc.grand_total -= vat_tax

	if doc.meta.get_field("rounded_total"):

		if doc.is_rounded_total_disabled():
			doc.outstanding_amount = doc.grand_total

		else:
			doc.rounded_total = round_based_on_smallest_currency_fraction(doc.grand_total,
				doc.currency, doc.precision("rounded_total"))
			doc.rounding_adjustment = flt(doc.rounded_total - doc.grand_total,
				doc.precision("rounding_adjustment"))
			doc.outstanding_amount = doc.rounded_total or doc.grand_total

	doc.in_words = money_in_words(doc.grand_total, doc.currency)
	doc.base_in_words = money_in_words(doc.base_grand_total, erpnext.get_company_currency(doc.company))
	doc.set_payment_schedule()

def make_regional_gl_entries(gl_entries, doc):
	"""Hooked to make_regional_gl_entries in Purchase Invoice.It appends the region specific general ledger entries to the list of GL Entries."""
	country = frappe.get_cached_value('Company', doc.company, 'country')

	if country != 'United Arab Emirates':
		return gl_entries

	if doc.reverse_charge == 'Y':
		tax_accounts = get_tax_accounts(doc.company)
		for tax in doc.get('taxes'):
			if tax.category not in ("Total", "Valuation and Total"):
				continue
			gl_entries = make_gl_entry(tax, gl_entries, doc, tax_accounts)
	return gl_entries

def make_gl_entry(tax, gl_entries, doc, tax_accounts):
	dr_or_cr = "credit" if tax.add_deduct_tax == "Add" else "debit"
	if flt(tax.base_tax_amount_after_discount_amount)  and tax.account_head in tax_accounts:
		account_currency = get_account_currency(tax.account_head)

		gl_entries.append(doc.get_gl_dict({
				"account": tax.account_head,
				"cost_center": tax.cost_center,
				"posting_date": doc.posting_date,
				"against": doc.supplier,
				dr_or_cr: tax.base_tax_amount_after_discount_amount,
				dr_or_cr + "_in_account_currency": tax.base_tax_amount_after_discount_amount \
					if account_currency==doc.company_currency \
					else tax.tax_amount_after_discount_amount
			}, account_currency, item=tax
		))
	return gl_entries


def validate_returns(doc, method):
	"""Standard Rated expenses should not be set when Reverse Charge Applicable is set."""
	country = frappe.get_cached_value('Company', doc.company, 'country')
	if country != 'United Arab Emirates':
		return
	if doc.reverse_charge == 'Y' and  flt(doc.recoverable_standard_rated_expenses) != 0:
		frappe.throw(_(
			"Recoverable Standard Rated expenses should not be set when Reverse Charge Applicable is Y"
		))

# India Utils / check the code

@frappe.whitelist()
def get_gst_accounts(company=None, account_wise=False, only_reverse_charge=0, only_non_reverse_charge=0):
	filters={"parent": "GST Settings"}

	if company:
		filters.update({'company': company})
	if only_reverse_charge:
		filters.update({'is_reverse_charge_account': 1})
	elif only_non_reverse_charge:
		filters.update({'is_reverse_charge_account': 0})

	gst_accounts = frappe._dict()
	gst_settings_accounts = frappe.get_all("GST Account",
		filters=filters,
		fields=["cgst_account", "sgst_account", "igst_account", "cess_account"])

	if not gst_settings_accounts and not frappe.flags.in_test and not frappe.flags.in_migrate:
		frappe.throw(_("Please set GST Accounts in GST Settings"))

	for d in gst_settings_accounts:
		for acc, val in d.items():
			if not account_wise:
				gst_accounts.setdefault(acc, []).append(val)
			elif val:
				gst_accounts[val] = acc

	return gst_accounts

def validate_reverse_charge_transaction(doc, method):
	country = frappe.get_cached_value('Company', doc.company, 'country')

	if country != 'India':
		return

	base_gst_tax = 0
	base_reverse_charge_booked = 0

	if doc.reverse_charge == 'Y':
		gst_accounts = get_gst_accounts(doc.company, only_reverse_charge=1)
		reverse_charge_accounts = gst_accounts.get('cgst_account') + gst_accounts.get('sgst_account') \
			+ gst_accounts.get('igst_account')

		gst_accounts = get_gst_accounts(doc.company, only_non_reverse_charge=1)
		non_reverse_charge_accounts = gst_accounts.get('cgst_account') + gst_accounts.get('sgst_account') \
			+ gst_accounts.get('igst_account')

		for tax in doc.get('taxes'):
			if tax.account_head in non_reverse_charge_accounts:
				if tax.add_deduct_tax == 'Add':
					base_gst_tax += tax.base_tax_amount_after_discount_amount
				else:
					base_gst_tax += tax.base_tax_amount_after_discount_amount
			elif tax.account_head in reverse_charge_accounts:
				if tax.add_deduct_tax == 'Add':
					base_reverse_charge_booked += tax.base_tax_amount_after_discount_amount
				else:
					base_reverse_charge_booked += tax.base_tax_amount_after_discount_amount

		if base_gst_tax != base_reverse_charge_booked:
			msg = _("Booked reverse charge is not equal to applied tax amount")
			msg += "<br>"
			msg += _("Please refer {gst_document_link} to learn more about how to setup and create reverse charge invoice").format(
				gst_document_link='<a href="https://docs.erpnext.com/docs/user/manual/en/regional/india/gst-setup">GST Documentation</a>')

			frappe.throw(msg)


def update_itc_availed_fields(doc, method):
	country = frappe.get_cached_value('Company', doc.company, 'country')

	if country != 'India':
		return

	# Initialize values
	doc.itc_integrated_tax = doc.itc_state_tax = doc.itc_central_tax = doc.itc_cess_amount = 0
	gst_accounts = get_gst_accounts(doc.company, only_non_reverse_charge=1)

	for tax in doc.get('taxes'):
		if tax.account_head in gst_accounts.get('igst_account', []):
			doc.itc_integrated_tax += flt(tax.base_tax_amount_after_discount_amount)
		if tax.account_head in gst_accounts.get('sgst_account', []):
			doc.itc_state_tax += flt(tax.base_tax_amount_after_discount_amount)
		if tax.account_head in gst_accounts.get('cgst_account', []):
			doc.itc_central_tax += flt(tax.base_tax_amount_after_discount_amount)
		if tax.account_head in gst_accounts.get('cess_account', []):
			doc.itc_cess_amount += flt(tax.base_tax_amount_after_discount_amount)

def update_taxable_values(doc, method):
	country = frappe.get_cached_value('Company', doc.company, 'country')

	if country != 'India':
		return

	gst_accounts = get_gst_accounts(doc.company)

	# Only considering sgst account to avoid inflating taxable value
	gst_account_list = gst_accounts.get('sgst_account', []) + gst_accounts.get('sgst_account', []) \
		+ gst_accounts.get('igst_account', [])

	additional_taxes = 0
	total_charges = 0
	item_count = 0
	considered_rows = []

	for tax in doc.get('taxes'):
		prev_row_id = cint(tax.row_id) - 1
		if tax.account_head in gst_account_list and prev_row_id not in considered_rows:
			if tax.charge_type == 'On Previous Row Amount':
				additional_taxes += doc.get('taxes')[prev_row_id].tax_amount_after_discount_amount
				considered_rows.append(prev_row_id)
			if tax.charge_type == 'On Previous Row Total':
				additional_taxes += doc.get('taxes')[prev_row_id].base_total - doc.base_net_total
				considered_rows.append(prev_row_id)

	for item in doc.get('items'):
		proportionate_value = item.base_net_amount if doc.base_net_total else item.qty
		total_value = doc.base_net_total if doc.base_net_total else doc.total_qty

		applicable_charges = flt(flt(proportionate_value * (flt(additional_taxes) / flt(total_value)),
			item.precision('taxable_value')))
		item.taxable_value = applicable_charges + proportionate_value
		total_charges += applicable_charges
		item_count += 1

	if total_charges != additional_taxes:
		diff = additional_taxes - total_charges
		doc.get('items')[item_count - 1].taxable_value += diff
