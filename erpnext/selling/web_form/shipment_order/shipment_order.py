from __future__ import unicode_literals

import frappe


def get_context(context):
    params = frappe.form_dict
    if('f' in params):
        context.f = 1;
    else:
        context.f = 0;

    return context
