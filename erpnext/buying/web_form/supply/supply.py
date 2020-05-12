from __future__ import unicode_literals

import frappe
import json


def get_context(context):
    # do your magic here
    if(frappe.form_dict.type):
        context.type = frappe.form_dict.type.lower()
    pass
