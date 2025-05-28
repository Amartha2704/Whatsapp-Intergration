# import frappe
# import requests
# from frappe.model.document import Document

# class WhatsAppMessage(Document):
#     pass


# @frappe.whitelist()
# def send_whatsapp_message(docname):
#     doc = frappe.get_doc("WhatsApp Message", docname)

#     url = "https://api.gupshup.io/sm/api/v1/msg"
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "apikey": "qpk4f7vilyb0ef8oeawrflbsap055zmt"  # ✅ Use environment variable in production
#     }

#     payload = {
#         "channel": "whatsapp",
#         "source": doc.source,  # ✅ Your Gupshup-approved sender number
#         "destination": doc.destination,
#         "message": doc.message,
#         "src.name": "Samyoga"  # ✅ Your registered Gupshup bot name
#     }

#     try:
#         response = requests.post(url, headers=headers, data=payload)
#         response.raise_for_status()  # Raises HTTPError if response code is not 200

#         # Optional: Save response or mark doc as sent
#         frappe.msgprint("✅ WhatsApp message sent successfully.")

#     except requests.exceptions.HTTPError as e:
#         frappe.throw(f"❌ HTTP error: {e.response.text}")
#     except Exception as e:
#         frappe.throw(f"❌ Failed to send message: {str(e)}")
import frappe
import requests
from frappe.model.document import Document

class WhatsAppMessage(Document):
    pass
@frappe.whitelist()
def send_whatsapp_message(docname):
    doc = frappe.get_doc("WhatsApp Message", docname)
    url = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": "qpk4f7vilyb0ef8oeawrflbsap055zmt"
    }
    payload = {
        "channel": "whatsapp",
        "source": doc.source,
        "destination": doc.destination,
        "message": doc.message,
        "src.name": "Samyoga"
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        # Parse JSON response
        response_data = response.json()
        
        # Extract status and messageId from response
        status_value = response_data.get("status", "")
        message_id = response_data.get("messageId", "")
        
        # Update document fields
        doc.status = status_value
        doc.message_id = message_id
        doc.content = "WhatsApp message sent successfully"
        
        # Save the document with updated fields
        doc.save(ignore_permissions=True)
        
        # Submit the document if it's not already submitted
        if doc.docstatus == 0:  # 0 means draft
            doc.submit()
        
        # Show success message to user
       # frappe.msgprint(f"✅ WhatsApp message sent successfully.\nStatus: {status_value}\nMessage ID: {message_id}", 
                       #indicator="green", alert=True)
        
        # Return values to update the frontend
        return {
            "status": "success",
            "message": "WhatsApp message sent successfully",
            "status_value": status_value,
            "message_id": message_id,
            "docname": docname,
            "submitted": True
        }
    except requests.exceptions.HTTPError as e:
        frappe.throw(f"❌ HTTP error: {e.response.text}")
    except Exception as e:
        frappe.throw(f"❌ Failed to send message: {str(e)}")


