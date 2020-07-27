import frappe
import json
from datetime import date, datetime



@frappe.whitelist()
def createTemplate(data):
    data = json.loads(data)
    template=frappe.get_doc({
        "doctype":"Pdf Document",
        "content":data['template'],
        "type":data['type']

    })

    # template.insert()
    # frappe.db.commit()

    return {'status': 'ok', 'template': template}


@frappe.whitelist()
def updateTemplate(data):
    data = json.loads(data)
    template=frappe.get_all("Pdf Document",filters={"type":data['type']},fields=["content","type","name"])

    frappe.db.set_value('Pdf Document',template[0]["name"], 'content',data["template"])
    # template[0]["content"]=data["template"]

    # template[0].save()


    # template.insert()
    frappe.db.commit()

    return {'status': 'ok', 'template': template}


@frappe.whitelist()
def getTemplate(data):
    data = json.loads(data)
    template=frappe.get_all("Pdf Document",filters={"type":data['type']},fields=["content","type","name"])

    # frappe.db.set_value('Pdf Document',template[0]["name"], 'content',data["template"])
    # template[0]["content"]=data["template"]

    # template[0].save()


    # template.insert()
    # frappe.db.commit()

    return {'status': 'ok', 'template': template[0]['content']}