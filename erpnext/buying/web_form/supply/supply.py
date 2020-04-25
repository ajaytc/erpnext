from __future__ import unicode_literals

import frappe
import json


def get_context(context):
    # do your magic here
    context.type = frappe.form_dict.type
    pass
