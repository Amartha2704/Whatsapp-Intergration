import frappe
from frappe import _

@frappe.whitelist()
def get_templates():
    """Get all WhatsApp templates"""
    templates = frappe.get_all(
        "WhatsApp Template",
        fields=["name", "template_name", "template_id", "template_type", 
                "approval_status", "language", "content"],
        order_by="creation desc"
    )
    
    return templates

@frappe.whitelist()
def submit_template_for_approval(template_name):
    """Submit a template for approval with Gupshup"""
    if not frappe.has_permission("WhatsApp Template", "write"):
        frappe.throw(_("You don't have permission to manage WhatsApp templates"))
    
    template = frappe.get_doc("WhatsApp Template", template_name)
    
    # In a real implementation, this would call Gupshup API to submit the template
    # For this example, we'll just simulate the process
    
    template.approval_status = "Pending"
    template.save()
    
    return {"success": True, "message": "Template submitted for approval"}