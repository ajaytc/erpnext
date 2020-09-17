from __future__ import unicode_literals
import frappe
import ast
import erpnext
from datetime import datetime
from frappe.utils import flt, nowdate, add_days, cint
from frappe import _
import frappe
import json


@frappe.whitelist()
def order_reminder(data):
    fabric_order_reminder()
    trimming_order_reminder()
    packaging_order_reminder()

def cron_order_reminder():
    fabric_order_reminder()
    trimming_order_reminder()
    packaging_order_reminder()


def fabric_order_reminder():

    doc_list = frappe.get_all("Fabric Order",
                              or_filters=[["confirmation_reminder", "=", nowdate()], ["profoma_reminder", "=", nowdate()], ["payment_reminder", "=", nowdate()], [
                                  "shipment_reminder", "=", nowdate()], ["reception_reminder", "=", nowdate()]],
                              fields=["confirmation_reminder", "profoma_reminder", "payment_reminder", "shipment_reminder", "reception_reminder", "name"])

    for fabricReminder in doc_list:
        now = frappe.format(nowdate(), {'fieldtype': 'Date'})

        if(frappe.format(fabricReminder.confirmation_reminder, {'fieldtype': 'Date'}) == now):
            confReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": fabricReminder.name,
                "type": "confirmation",
                "order_type": "fabric"
            })

            confReminder.insert()

        if (frappe.format(fabricReminder.profoma_reminder, {'fieldtype': 'Date'}) == now):
            profReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": fabricReminder.name,
                "type": "profoma",
                "order_type": "fabric"
            })

            profReminder.insert()

        if (frappe.format(fabricReminder.payment_reminder, {'fieldtype': 'Date'}) == now):
            paymReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": fabricReminder.name,
                "type": "payment",
                "order_type": "fabric"
            })

            paymReminder.insert()

        if (frappe.format(fabricReminder.shipment_reminder, {'fieldtype': 'Date'}) == now):
            shipReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": fabricReminder.name,
                "type": "shipment",
                "order_type": "fabric"
            })

            shipReminder.insert()

        if (frappe.format(fabricReminder.reception_reminder, {'fieldtype': 'Date'}) == now):
            recepReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": fabricReminder.name,
                "type": "reception",
                "order_type": "fabric"
            })

            recepReminder.insert()

    return doc_list


def trimming_order_reminder():

    doc_list = frappe.get_all("Trimming Order",
                              or_filters=[["confirmation_reminder", "=", nowdate()], ["profoma_reminder", "=", nowdate()], ["payment_reminder", "=", nowdate()], [
                                  "shipment_reminder", "=", nowdate()], ["reception_reminder", "=", nowdate()]],
                              fields=["confirmation_reminder", "profoma_reminder", "payment_reminder", "shipment_reminder", "reception_reminder", "name"])

    for trimReminder in doc_list:
        now = frappe.format(nowdate(), {'fieldtype': 'Date'})

        if(frappe.format(trimReminder.confirmation_reminder, {'fieldtype': 'Date'}) == now):
            confReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": trimReminder.name,
                "type": "confirmation",
                "order_type": "trimming"
            })

            confReminder.insert()

        if (frappe.format(trimReminder.profoma_reminder, {'fieldtype': 'Date'}) == now):
            profReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": trimReminder.name,
                "type": "profoma",
                "order_type": "trimming"
            })

            profReminder.insert()

        if (frappe.format(trimReminder.payment_reminder, {'fieldtype': 'Date'}) == now):
            paymReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": trimReminder.name,
                "type": "payment",
                "order_type": "trimming"
            })

            paymReminder.insert()

        if (frappe.format(trimReminder.shipment_reminder, {'fieldtype': 'Date'}) == now):
            shipReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": trimReminder.name,
                "type": "shipment",
                "order_type": "trimming"
            })

            shipReminder.insert()

        if (frappe.format(trimReminder.reception_reminder, {'fieldtype': 'Date'}) == now):
            recepReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": trimReminder.name,
                "type": "reception",
                "order_type": "trimming"
            })

            recepReminder.insert()

    return doc_list


def packaging_order_reminder():
    doc_list = frappe.get_all("Packaging Order",
                              or_filters=[["confirmation_reminder", "=", nowdate()], ["profoma_reminder", "=", nowdate()], ["payment_reminder", "=", nowdate()], [
                                  "shipment_reminder", "=", nowdate()], ["reception_reminder", "=", nowdate()]],
                              fields=["confirmation_reminder", "profoma_reminder", "payment_reminder", "shipment_reminder", "reception_reminder", "name"])

    for packReminder in doc_list:
        now = frappe.format(nowdate(), {'fieldtype': 'Date'})

        if(frappe.format(packReminder.confirmation_reminder, {'fieldtype': 'Date'}) == now):
            confReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": packReminder.name,
                "type": "confirmation",
                "order_type": "packaging"
            })

            confReminder.insert()

        if (frappe.format(packReminder.profoma_reminder, {'fieldtype': 'Date'}) == now):
            profReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": packReminder.name,
                "type": "profoma",
                "order_type": "packaging"
            })

            profReminder.insert()

        if (frappe.format(packReminder.payment_reminder, {'fieldtype': 'Date'}) == now):
            paymReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": packReminder.name,
                "type": "payment",
                "order_type": "packaging"
            })

            paymReminder.insert()

        if (frappe.format(packReminder.shipment_reminder, {'fieldtype': 'Date'}) == now):
            shipReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": packReminder.name,
                "type": "shipment",
                "order_type": "packaging"
            })

            shipReminder.insert()

        if (frappe.format(packReminder.reception_reminder, {'fieldtype': 'Date'}) == now):
            recepReminder = frappe.get_doc({
                "doctype": "Reminder",
                "order": packReminder.name,
                "type": "reception",
                "order_type": "packaging"
            })

            recepReminder.insert()

    return doc_list


@frappe.whitelist()
def markSeen(data):
    data = json.loads(data)
    if(data['reminder'] == 'fabric_reminder'):
        orderType = "fabric"

    elif(data['reminder'] == 'trimming_reminder'):
        orderType = "trimming"
    elif (data['reminder'] == 'pack_reminder'):
        orderType = "packaging"

    unseenReminders = frappe.db.sql("update `tabReminder` set seen='1' where seen='0' and  order_type='"+orderType+"'")



    return unseenReminders

@frappe.whitelist()
def deleteReminder(reminderslist):
    reminderslist = ast.literal_eval(reminderslist)
    temp_reminders = []
    for rem_name in reminderslist:
        temp_reminders.append(frappe.get_doc('Reminder',rem_name))
    for reminder in temp_reminders:
        frappe.delete_doc('Reminder',reminder.name)
    frappe.db.commit()
    return {'status': 'ok', 'item': temp_reminders}