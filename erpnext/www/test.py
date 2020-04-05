
from __future__ import unicode_literals
import frappe

sitemap = 1

def get_context(context):
	context.doc = frappe.get_doc("About Us Settings", "About Us Settings")
    context.users = frappe.get_all('User')

	context.parents = [
		{ "name": frappe._("Home"), "route": "/" }
	]

	return context
