import frappe
from frappe import _
import json
from datetime import datetime, timedelta
@frappe.whitelist()
def send_message(contact, message, message_type="TEXT", media_url=None):
    # TODO: Implement sending message via Gupshup API or your WhatsApp provider
    # For now, just return a dummy success response
    return {
        "status": "success",
        "contact": contact,
        "message": message,
        "message_type": message_type,
        "media_url": media_url,
        "sent_at": "now"
    }
@frappe.whitelist()
def send_template_message(contact, template, params=None):
    # TODO: Implement sending template message via Gupshup API or your WhatsApp provider
    return {
        "status": "success",
        "contact": contact,
        "template": template,
        "params": params,
        "sent_at": "now"
    }

