import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def execute():
    if not frappe.db.exists("Custom Field", "User-whatsapp_access"):
        create_custom_field("User", {
            "label": "WhatsApp Access",
            "fieldname": "whatsapp_access",
            "fieldtype": "Check",  # or "Data" for phone number
            "insert_after": "email",
        })
