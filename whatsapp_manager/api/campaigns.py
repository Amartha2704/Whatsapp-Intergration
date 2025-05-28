import frappe
from frappe import _

@frappe.whitelist()
def get_campaigns():
    """Get all WhatsApp campaigns"""
    campaigns = frappe.get_all(
        "WhatsApp Campaign",
        fields=["name", "campaign_name", "status", "template", 
                "schedule_date", "total_sent", "delivered", 
                "read", "responses"],
        order_by="creation desc"
    )
    
    return campaigns

@frappe.whitelist()
def schedule_campaign(campaign_name, schedule_date=None):
    """Schedule a campaign for sending"""
    if not frappe.has_permission("WhatsApp Campaign", "write"):
        frappe.throw(_("You don't have permission to manage WhatsApp campaigns"))
    
    campaign = frappe.get_doc("WhatsApp Campaign", campaign_name)
    
    if schedule_date:
        campaign.schedule_date = schedule_date
    
    campaign.status = "Scheduled"
    campaign.save()
    
    return {"success": True, "message": "Campaign scheduled successfully"}