import frappe
import json
from datetime import date, datetime


def createTemplate(data):
    data = json.loads(data)
    template = frappe.get_doc({
        "doctype": "Pdf Document",
        "content": data['template'],
        "type": data['type']

    })

    # template.insert()
    # frappe.db.commit()

    return {'status': 'ok', 'template': template}


@frappe.whitelist()
def updateTemplate(data):
    data = json.loads(data)
    if(data['case'] == 'email'):
        updateNotificationTemplate(data)
    elif (data['case'] == 'pdf'):
        updatePdfTemplate(data)






def updatePdfTemplate(data):
    template = frappe.get_doc("Pdf Document",data['name'])

    frappe.db.set_value(
        'Pdf Document', template.name, 'content', data["template"])
    frappe.db.commit()
    return {'status': 'ok', 'template': template}


def updateNotificationTemplate(data):
    notification = frappe.get_doc('Notification', data['name'])

    frappe.db.set_value('Notification', notification.name,
                        'message', data['template'])
    updateSubject(data,notification)
    frappe.db.commit()
    return {'status': 'ok', 'template': notification}

def updateSubject(data,notification):
    frappe.db.set_value('Notification', notification.name,
                        'subject', data['subject'])


@frappe.whitelist()
def getPdfTemplate(data):
    data = json.loads(data)
    template = frappe.get_doc("Pdf Document",data['name'])

    # frappe.db.set_value('Pdf Document',template[0]["name"], 'content',data["template"])
    # template[0]["content"]=data["template"]

    # template[0].save()

    # template.insert()
    # frappe.db.commit()

    return {'status': 'ok', 'template': template}


@frappe.whitelist()
def getEmailTemplate(data):
    data = json.loads(data)
    template = frappe.get_doc("Notification",data['name'])

    # frappe.db.set_value('Pdf Document',template[0]["name"], 'content',data["template"])
    # template[0]["content"]=data["template"]

    # template[0].save()

    # template.insert()
    # frappe.db.commit()

    return {'status': 'ok', 'template': template}