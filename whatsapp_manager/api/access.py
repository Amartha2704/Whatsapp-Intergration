import frappe
from frappe import _

@frappe.whitelist()
def check_whatsapp_access():
    """Check if the current user has WhatsApp access"""
    user = frappe.session.user
    
    # System Manager always has access
    if "System Manager" in frappe.get_roles(user):
        return {"has_access": True}
    cd ..
    # Check user's WhatsApp access setting
    access = frappe.db.get_value("User", user, "whatsapp_access")
    
    return {"has_access": access == 1}