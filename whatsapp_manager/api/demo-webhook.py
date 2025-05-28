import frappe
from frappe import _
import json
from whatsapp_manager.api.chat import handle_incoming_message




@frappe.whitelist(allow_guest=True)
def gupshup_webhook():
    data = frappe.local.form_dict

    if data.get("type") == "message":
        payload = data.get("payload", {})
        source = payload.get("source")
        destination = payload.get("destination")
        message = payload.get("payload", {}).get("text")  # Nested payload

        if not source or not destination:
            frappe.throw("Error: Value missing for WhatsApp Message: source or destination")

        frappe.log_error(
            f"Source: {source}, Destination: {destination}, Message: {message}",
            "Webhook Received"
        )

        return {
            "status": "success",
            "result": {
                "status": "logged",
                "message": "Message logged, chat functions not available"
            }
        }
    else:
        return {
            "status": "success",
            "message": "Unknown webhook type"
        }

# def gupshup_webhook():
#     """Handle incoming webhooks from Gupshup"""
#     try:
#         # Get the request data
#         data = frappe.local.form_dict
        
#         # Log the incoming webhook for debugging (with shorter title)
#         frappe.log_error(json.dumps(data, indent=2), "Gupshup Webhook")
        
#         # Handle different types of webhooks
#         webhook_type = data.get('type')
        
#         if webhook_type == 'message':
#             # Incoming message
#             result = handle_incoming_webhook_message(data)
#             return {"status": "success", "result": result}
#         elif webhook_type == 'message-event':
#             # Message status update (delivery, read, etc.)
#             result = handle_message_status_update(data)
#             return {"status": "success", "result": result}
#         else:
#             frappe.log_error(f"Unknown webhook type: {webhook_type}", "Unknown Webhook Type")
#             return {"status": "success", "message": "Unknown webhook type"}
            
#     except Exception as e:
#         frappe.log_error(str(e), "Webhook Error")
#         return {"status": "error", "message": str(e)}

def handle_incoming_webhook_message(data):
    """Process incoming message webhook"""
    try:
        # Extract message data
        payload = data.get('payload', {})
        
        phone_number = payload.get('source')
        message_type_raw = payload.get('type', 'text').lower()
        gupshup_message_id = payload.get('id')
        
        # Map Gupshup message types to your DocType options
        message_type_mapping = {
            'text': 'Text',
            'image': 'Image',
            'video': 'Video',
            'audio': 'Audio',
            'document': 'Document',
            'location': 'Location'
        }
        
        # Get the correct message type for your DocType
        message_type = message_type_mapping.get(message_type_raw, 'Text')
        
        # Extract message content based on type
        if message_type_raw == 'text':
            message_content = payload.get('payload', {}).get('text', '')
            media_url = None
            media_type = None
        elif message_type_raw in ['image', 'video', 'audio', 'document']:
            message_content = payload.get('payload', {}).get('caption', '')
            media_url = payload.get('payload', {}).get('url')
            media_type = message_type_raw
        elif message_type_raw == 'location':
            location_data = payload.get('payload', {})
            message_content = f"Location: {location_data.get('latitude')}, {location_data.get('longitude')}"
            media_url = None
            media_type = None
        elif message_type_raw == 'contact':
            contact_data = payload.get('payload', {})
            message_content = f"Contact: {contact_data.get('name')}"
            media_url = None
            media_type = None
        else:
            message_content = "Unsupported message type"
            media_url = None
            media_type = None
        
        # Try to create the incoming message record with corrected import
        try:
            # Import using the correct path
            handle_incoming_message = frappe.get_attr("whatsapp_manager.api.chat.handle_incoming_message")
            result = handle_incoming_message(
                phone_number=phone_number,
                message=message_content,
                message_type=message_type,  # Use the mapped message type
                media_url=media_url,
                media_type=media_type,
                gupshup_message_id=gupshup_message_id
            )
            return result
        except Exception as import_error:
            # If import fails, try alternative import path
            try:
                from whatsapp_manager.api.chat import handle_incoming_message
                result = handle_incoming_message(
                    phone_number=phone_number,
                    message=message_content,
                    message_type=message_type,  # Use the mapped message type
                    media_url=media_url,
                    media_type=media_type,
                    gupshup_message_id=gupshup_message_id
                )
                return result
            except Exception as e2:
                # If both imports fail, log the message
                frappe.log_error(f"Import error: {str(import_error)}, Alternative error: {str(e2)}", "Import Error")
                frappe.log_error(f"Incoming message from {phone_number}: {message_content}", "Incoming Message")
                return {"status": "logged", "message": "Message logged, chat functions not available"}
        
    except Exception as e:
        frappe.log_error(str(e), "Incoming Message Error")
        return {"status": "error", "message": str(e)}
def handle_message_status_update(data):
    """Process message status update webhook"""
    try:
        # Extract status data
        payload = data.get('payload', {})
        
        gupshup_message_id = payload.get('gsId')
        status = payload.get('type', '').title()  # delivered, read, failed, etc.
        
        # Map Gupshup status to our status
        status_mapping = {
            'Enroute': 'Sent',
            'Delivered': 'Delivered',
            'Read': 'Read',
            'Failed': 'Failed',
            'Sent': 'Sent'
        }
        
        mapped_status = status_mapping.get(status, status)
        
        # Try to update message status
        try:
            update_message_status = frappe.get_attr("whatsapp_manager.api.chat.update_message_status")
            result = update_message_status(gupshup_message_id, mapped_status)
            return result
        except Exception:
            # If chat functions don't exist yet, just log the status
            frappe.log_error(f"Status update for {gupshup_message_id}: {mapped_status}", "Status Update")
            return {"status": "logged", "message": "Status logged, chat functions not available"}
        
    except Exception as e:
        frappe.log_error(str(e), "Status Update Error")
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def gupshup_opt_in_webhook():
    """Handle opt-in webhooks from Gupshup"""
    try:
        data = frappe.local.form_dict
        
        phone_number = data.get('mobile')
        opt_in_status = data.get('optin')  # true/false
        
        if phone_number:
            # Clean phone number
            if not phone_number.startswith("+"):
                phone_number = "+" + phone_number
                
            # Update or create contact
            existing_contact = frappe.get_all(
                "WhatsApp Contact",
                filters={"phone_number": phone_number},
                limit=1
            )
            
            status = "Opted In" if opt_in_status == "true" else "Opted Out"
            
            if existing_contact:
                frappe.db.set_value("WhatsApp Contact", existing_contact[0].name, "opt_in_status", status)
            else:
                # Create new contact
                contact_doc = frappe.get_doc({
                    "doctype": "WhatsApp Contact",
                    "phone_number": phone_number,
                    "name1": phone_number,
                    "opt_in_status": status
                })
                contact_doc.insert(ignore_permissions=True)
                
            frappe.db.commit()
        
        return {"status": "success"}
        
    except Exception as e:
        frappe.log_error(str(e), "Opt-in Error")
        return {"status": "error", "message": str(e)}
    # File: whatsapp_manager/api/webhook.py
# Fixed webhook handler - resolves destination contact issue

# import frappe
# from frappe import _
# import json
# from datetime import datetime

# @frappe.whitelist(allow_guest=True)
# def handle_gupshup_webhook():
#     """
#     Main webhook endpoint to receive incoming WhatsApp messages from Gupshup
#     URL: https://smartschool.prismaticsoft.com/api/method/whatsapp_manager.api.webhook.handle_gupshup_webhook
#     """
#     try:
#         # Get the request data
#         if frappe.request.method != 'POST':
#             return {"status": "error", "message": "Only POST method allowed"}
        
#         # Get JSON data from request
#         data = frappe.request.get_json()
        
#         if not data:
#             # Try to get form data if JSON is not available
#             data = frappe.local.form_dict
        
#         # Log the received data for debugging
#         frappe.log_error(f"Webhook received data: {json.dumps(data, indent=2)}", "WhatsApp Webhook")
        
#         # Extract message information from Gupshup webhook
#         message_type = data.get('type', 'message')
        
#         if message_type == 'message':
#             return process_incoming_message(data)
#         elif message_type == 'message-event':
#             return process_delivery_report(data)
#         else:
#             frappe.log_error(f"Unknown webhook type: {message_type}", "WhatsApp Webhook")
#             return {"status": "ignored", "message": f"Unknown type: {message_type}"}
            
#     except Exception as e:
#         frappe.log_error(f"Webhook error: {str(e)}", "WhatsApp Webhook Error")
#         return {"status": "error", "message": str(e)}

# def process_incoming_message(data):
#     """Process incoming WhatsApp message"""
#     try:
#         # Extract message details from Gupshup webhook format
#         payload = data.get('payload', {})
        
#         # Source phone number (sender)
#         source_phone = payload.get('source', '')
        
#         # Message content
#         message_payload = payload.get('payload', {})
#         message_text = ""
#         message_type = "Text"
#         media_url = None
#         media_type = None
        
#         # Handle different message types
#         if message_payload.get('type') == 'text':
#             message_text = message_payload.get('text', '')
#         elif message_payload.get('type') == 'image':
#             message_text = message_payload.get('caption', 'Image')
#             message_type = "Image"
#             media_url = message_payload.get('url', '')
#             media_type = "image"
#         elif message_payload.get('type') == 'audio':
#             message_text = "Audio message"
#             message_type = "Audio"
#             media_url = message_payload.get('url', '')
#             media_type = "audio"
#         elif message_payload.get('type') == 'video':
#             message_text = message_payload.get('caption', 'Video')
#             message_type = "Video"
#             media_url = message_payload.get('url', '')
#             media_type = "video"
#         elif message_payload.get('type') == 'file':
#             message_text = f"Document: {message_payload.get('filename', 'file')}"
#             message_type = "Document"
#             media_url = message_payload.get('url', '')
#             media_type = "document"
#         elif message_payload.get('type') == 'location':
#             lat = message_payload.get('latitude', 0)
#             lng = message_payload.get('longitude', 0)
#             message_text = f"Location: {lat}, {lng}"
#             message_type = "Location"
#         else:
#             message_text = str(message_payload)
        
#         # Gupshup message ID
#         gupshup_message_id = payload.get('id', '')
        
#         # Clean source phone number
#         clean_source = source_phone.replace('+', '') if source_phone.startswith('+') else source_phone
        
#         frappe.log_error(f"Processing incoming message from {clean_source}: {message_text}", "WhatsApp Incoming")
        
#         # Create incoming message document
#         result = create_incoming_message_doc(
#             source_phone=clean_source,
#             message=message_text,
#             message_type=message_type,
#             media_url=media_url,
#             media_type=media_type,
#             gupshup_message_id=gupshup_message_id
#         )
        
#         return result
        
#     except Exception as e:
#         frappe.log_error(f"Error processing incoming message: {str(e)}", "WhatsApp Incoming Error")
#         return {"status": "error", "message": str(e)}

# def create_incoming_message_doc(source_phone, message, message_type="Text", 
#                                media_url=None, media_type=None, gupshup_message_id=None):
#     """Create WhatsApp Message document for incoming message"""
#     try:
#         # Get or create contacts for both source and destination
#         source_contact = get_or_create_contact_simple(source_phone)
#         destination_contact = get_or_create_business_contact()
        
#         # Check for duplicate messages
#         if gupshup_message_id:
#             existing = frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id})
#             if existing:
#                 return {"status": "duplicate", "message": "Message already exists"}
        
#         # Generate message ID if not provided
#         if not gupshup_message_id:
#             gupshup_message_id = f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
#         # Create WhatsApp Message document with flexible field handling
#         message_data = {
#             "doctype": "WhatsApp Message",
#             "source": source_phone,
#             "message": message,
#             "message_id": gupshup_message_id,
#             "direction": "Incoming",
#             "message_type": message_type,
#             "status": "Delivered",
#             "timestamp": datetime.now(),
#             "content": f"Received: {message}"[:100]
#         }
        
#         # Add destination fields based on what exists
#         if destination_contact:
#             message_data["destination"] = destination_contact
#         else:
#             # If destination contact doesn't exist, use phone number
#             message_data["destination"] = "919746574552"
        
#         # Add optional fields if they exist
#         if media_url:
#             message_data["media_url"] = media_url
#         if media_type:
#             message_data["media_type"] = media_type
            
#         # Add contact field if source contact exists
#         if source_contact:
#             message_data["contact"] = source_contact
            
#         # Add destination_name if field exists
#         try:
#             message_data["destination_name"] = "Your Business"
#         except:
#             pass
        
#         message_doc = frappe.get_doc(message_data)
        
#         # Insert the document
#         message_doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         # Update last message date on contact if possible
#         try:
#             if source_contact:
#                 frappe.db.set_value("Whatsapp Contact", source_contact, "last_message_date", datetime.now())
#                 frappe.db.commit()
#         except:
#             pass  # Field might not exist
        
#         # Log success
#         frappe.log_error(f"Successfully created incoming message doc: {message_doc.name}", "WhatsApp Success")
        
#         return {
#             "status": "success", 
#             "message_doc_name": message_doc.name,
#             "contact": source_contact,
#             "destination_contact": destination_contact,
#             "message_id": gupshup_message_id,
#             "phone": source_phone,
#             "text": message
#         }
        
#     except Exception as e:
#         frappe.log_error(f"Error creating incoming message doc: {str(e)}", "WhatsApp Document Error")
#         return {"status": "error", "message": str(e)}

# def get_or_create_contact_simple(phone_number):
#     """Get or create Whatsapp Contact with error handling"""
#     try:
#         # Clean phone number
#         clean_phone = phone_number.replace('+', '') if phone_number.startswith('+') else phone_number
        
#         # Try to find existing contact
#         existing_contact = frappe.get_all(
#             "Whatsapp Contact",
#             filters={"phone_number": clean_phone},
#             fields=["name"],
#             limit=1
#         )
        
#         if existing_contact:
#             return existing_contact[0].name
#         else:
#             # Try to create new contact
#             try:
#                 contact_doc = frappe.get_doc({
#                     "doctype": "Whatsapp Contact",
#                     "phone_number": clean_phone,
#                     "name1": f"Contact {clean_phone[-4:]}"  # Use last 4 digits as name
#                 })
                
#                 # Add opt_in_status if field exists
#                 if hasattr(contact_doc, 'opt_in_status'):
#                     contact_doc.opt_in_status = "Opted In"
                
#                 contact_doc.insert(ignore_permissions=True)
#                 frappe.db.commit()
                
#                 return contact_doc.name
                
#             except Exception as contact_error:
#                 # If contact creation fails, log but don't fail the message
#                 frappe.log_error(f"Contact creation failed: {str(contact_error)}", "Contact Creation Error")
#                 return None
            
#     except Exception as e:
#         frappe.log_error(f"Error in get_or_create_contact: {str(e)}", "WhatsApp Contact Error")
#         return None

# def get_or_create_business_contact():
#     """Get or create your business contact for destination field"""
#     try:
#         business_phone = "919746574552"
        
#         # Try to find existing business contact
#         existing_contact = frappe.get_all(
#             "Whatsapp Contact",
#             filters={"phone_number": business_phone},
#             fields=["name"],
#             limit=1
#         )
        
#         if existing_contact:
#             return existing_contact[0].name
#         else:
#             # Try to create business contact
#             try:
#                 contact_doc = frappe.get_doc({
#                     "doctype": "Whatsapp Contact",
#                     "phone_number": business_phone,
#                     "name1": "Your Business"  # Business name
#                 })
                
#                 # Add opt_in_status if field exists
#                 if hasattr(contact_doc, 'opt_in_status'):
#                     contact_doc.opt_in_status = "Opted In"
                
#                 contact_doc.insert(ignore_permissions=True)
#                 frappe.db.commit()
                
#                 return contact_doc.name
                
#             except Exception as contact_error:
#                 # If business contact creation fails, log but continue
#                 frappe.log_error(f"Business contact creation failed: {str(contact_error)}", "Business Contact Error")
#                 return None
            
#     except Exception as e:
#         frappe.log_error(f"Error in get_or_create_business_contact: {str(e)}", "Business Contact Error")
#         return None

# def process_delivery_report(data):
#     """Process delivery report from Gupshup"""
#     try:
#         payload = data.get('payload', {})
#         message_id = payload.get('gsId', '')  # Gupshup message ID
#         event_type = payload.get('type', '')  # sent, delivered, read, failed
        
#         # Map Gupshup event types to our status
#         status_mapping = {
#             "sent": "Sent",
#             "delivered": "Delivered", 
#             "read": "Read",
#             "failed": "Failed"
#         }
        
#         new_status = status_mapping.get(event_type, "Sent")
        
#         # Find and update the message
#         message_docs = frappe.get_all(
#             "WhatsApp Message",
#             filters={"message_id": message_id},
#             fields=["name"],
#             limit=1
#         )
        
#         if message_docs:
#             frappe.db.set_value("WhatsApp Message", message_docs[0].name, "status", new_status)
#             frappe.db.commit()
            
#             frappe.log_error(f"Updated message {message_id} status to {new_status}", "WhatsApp Status Update")
#             return {"status": "success", "message": f"Status updated to {new_status}"}
#         else:
#             return {"status": "not_found", "message": "Message not found"}
            
#     except Exception as e:
#         frappe.log_error(f"Error processing delivery report: {str(e)}", "WhatsApp Delivery Error")
#         return {"status": "error", "message": str(e)}

# @frappe.whitelist()
# def test_webhook():
#     """Test webhook functionality"""
#     try:
#         # Simulate incoming message data
#         test_data = {
#             "type": "message",
#             "payload": {
#                 "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
#                 "source": "919876543210",
#                 "payload": {
#                     "type": "text",
#                     "text": "Test incoming message - destination issue fixed"
#                 }
#             }
#         }
        
#         result = process_incoming_message(test_data)
#         return {
#             "status": "success",
#             "message": "Webhook test completed",
#             "result": result
#         }
        
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# @frappe.whitelist()
# def get_recent_messages(contact_phone, limit=50):
#     """Get recent messages for a contact (for real-time updates)"""
#     try:
#         clean_phone = contact_phone.replace('+', '') if contact_phone.startswith('+') else contact_phone
#         our_number = "919746574552"
        
#         # Get messages where source or destination matches the contact
#         messages = frappe.get_all(
#             "WhatsApp Message",
#             filters=[
#                 ["OR", 
#                     [["source", "=", clean_phone], ["destination", "=", our_number]],
#                     [["source", "=", our_number], ["destination", "=", clean_phone]]
#                 ]
#             ],
#             fields=["name", "source", "destination", "message", "direction", "message_type", 
#                    "status", "timestamp", "message_id", "media_url", "media_type", "creation"],
#             order_by="creation desc",
#             limit=limit
#         )
        
#         return {
#             "status": "success",
#             "messages": messages
#         }
        
#     except Exception as e:
#         frappe.log_error(f"Error getting recent messages: {str(e)}", "WhatsApp Recent Messages Error")
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# # Legacy webhook function for compatibility
# @frappe.whitelist(allow_guest=True)
# def gupshup_webhook():
#     """Legacy webhook function - redirects to main handler"""
#     return handle_gupshup_webhook()

# @frappe.whitelist(allow_guest=True)
# def gupshup_opt_in_webhook():
#     """Handle opt-in webhooks from Gupshup"""
#     try:
#         data = frappe.local.form_dict
        
#         phone_number = data.get('mobile')
#         opt_in_status = data.get('optin')  # true/false
        
#         if phone_number:
#             # Clean phone number
#             clean_phone = phone_number.replace('+', '') if phone_number.startswith('+') else phone_number
                
#             # Update or create contact
#             existing_contact = frappe.get_all(
#                 "Whatsapp Contact",
#                 filters={"phone_number": clean_phone},
#                 limit=1
#             )
            
#             status = "Opted In" if opt_in_status == "true" else "Opted Out"
            
#             if existing_contact:
#                 try:
#                     frappe.db.set_value("Whatsapp Contact", existing_contact[0].name, "opt_in_status", status)
#                 except:
#                     pass  # Field might not exist
#             else:
#                 # Create new contact
#                 try:
#                     contact_doc = frappe.get_doc({
#                         "doctype": "Whatsapp Contact",
#                         "phone_number": clean_phone,
#                         "name1": clean_phone
#                     })
                    
#                     # Add opt_in_status if field exists
#                     if hasattr(contact_doc, 'opt_in_status'):
#                         contact_doc.opt_in_status = status
                    
#                     contact_doc.insert(ignore_permissions=True)
#                 except Exception as contact_error:
#                     frappe.log_error(f"Opt-in contact creation error: {str(contact_error)}", "Opt-in Error")
                
#             frappe.db.commit()
        
#         return {"status": "success"}
        
#     except Exception as e:
#         frappe.log_error(str(e), "Opt-in Error")
#         return {"status": "error", "message": str(e)}

# @frappe.whitelist()
# def send_test_message(destination, message):
#     """Test sending message via Gupshup API"""
#     try:
#         import urllib.parse
#         import urllib.request
#         import json
        
#         # Your Gupshup configuration
#         api_key = "qpk4f7vilyb0ef8oeawrflbsap055zmt"
#         source_number = "919746574552"
        
#         # Clean destination number
#         clean_destination = str(destination).replace("+", "")
#         if not clean_destination.startswith('91') and len(clean_destination) == 10:
#             clean_destination = '91' + clean_destination
        
#         # Prepare message data for Gupshup
#         message_data = {
#             'type': 'text',
#             'text': str(message)
#         }
        
#         # Prepare form data for Gupshup API
#         form_data = {
#             'channel': 'whatsapp',
#             'source': source_number,
#             'destination': clean_destination,
#             'message': json.dumps(message_data),
#             'src.name': 'smartschool'
#         }
        
#         # Encode the data
#         data = urllib.parse.urlencode(form_data).encode('utf-8')
        
#         # Create the request
#         req = urllib.request.Request(
#             'https://api.gupshup.io/sm/api/v1/msg',
#             data=data,
#             headers={
#                 'apikey': api_key,
#                 'Content-Type': 'application/x-www-form-urlencoded'
#             }
#         )
        
#         # Make the API call
#         with urllib.request.urlopen(req, timeout=30) as response:
#             response_data = response.read().decode('utf-8')
            
#         # Also create record in WhatsApp Message doctype
#         message_id = f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
#         message_doc = frappe.get_doc({
#             "doctype": "WhatsApp Message",
#             "source": source_number,
#             "destination": clean_destination,
#             "message": message,
#             "message_id": message_id,
#             "direction": "Outgoing",
#             "message_type": "Text",
#             "status": "Sent",
#             "timestamp": datetime.now(),
#             "content": f"Sent via Gupshup: {response_data}"[:100]
#         })
        
#         message_doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "Message sent successfully",
#             "gupshup_response": response_data,
#             "frappe_doc": message_doc.name,
#             "message_id": message_id,
#             "destination": clean_destination
#         }
        
#     except Exception as e:
#         frappe.log_error(f"Send test message error: {str(e)}", "Send Test Error")
#         return {
#             "success": False,
#             "error": str(e)
#         }       


# File: whatsapp_manager/api/webhook.py
# Complete WhatsApp webhook handler with Gupshup integration

import frappe
from frappe import _
import json
import urllib.parse
import urllib.request
from datetime import datetime

# Gupshup Configuration
GUPSHUP_CONFIG = {
    "api_key": "qpk4f7vilyb0ef8oeawrflbsap055zmt",
    "source_number": "919746574552",
    "api_endpoint": "https://api.gupshup.io/sm/api/v1/msg",
    "app_name": "smartschool"
}

@frappe.whitelist(allow_guest=True)
def handle_gupshup_webhook():
    """
    Main webhook endpoint to receive incoming WhatsApp messages from Gupshup
    URL: https://smartschool.prismaticsoft.com/api/method/whatsapp_manager.api.webhook.handle_gupshup_webhook
    """
    try:
        # Get the request data
        if frappe.request.method != 'POST':
            return {"status": "error", "message": "Only POST method allowed"}
        
        # Get JSON data from request
        data = frappe.request.get_json()
        
        if not data:
            # Try to get form data if JSON is not available
            data = frappe.local.form_dict
        
        # Log the received data for debugging
        frappe.log_error(f"Webhook received data: {json.dumps(data, indent=2)}", "WhatsApp Webhook")
        
        # Extract message information from webhook
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            return process_incoming_message(data)
        elif message_type == 'message-event':
            return process_delivery_report(data)
        else:
            frappe.log_error(f"Unknown webhook type: {message_type}", "WhatsApp Webhook")
            return {"status": "ignored", "message": f"Unknown type: {message_type}"}
            
    except Exception as e:
        frappe.log_error(f"Webhook error: {str(e)}", "WhatsApp Webhook Error")
        return {"status": "error", "message": str(e)}

def process_incoming_message(data):
    """Process incoming WhatsApp message"""
    try:
        # Extract message details from webhook format
        payload = data.get('payload', {})
        
        # Source phone number (sender)
        source_phone = payload.get('source', '')
        
        # Message content
        message_payload = payload.get('payload', {})
        message_text = ""
        message_type = "Text"
        media_url = None
        media_type = None
        
        # Handle different message types
        if message_payload.get('type') == 'text':
            message_text = message_payload.get('text', '')
        elif message_payload.get('type') == 'image':
            message_text = message_payload.get('caption', 'Image')
            message_type = "Image"
            media_url = message_payload.get('url', '')
            media_type = "image"
        elif message_payload.get('type') == 'audio':
            message_text = "Audio message"
            message_type = "Audio"
            media_url = message_payload.get('url', '')
            media_type = "audio"
        elif message_payload.get('type') == 'video':
            message_text = message_payload.get('caption', 'Video')
            message_type = "Video"
            media_url = message_payload.get('url', '')
            media_type = "video"
        elif message_payload.get('type') == 'file':
            message_text = f"Document: {message_payload.get('filename', 'file')}"
            message_type = "Document"
            media_url = message_payload.get('url', '')
            media_type = "document"
        elif message_payload.get('type') == 'location':
            lat = message_payload.get('latitude', 0)
            lng = message_payload.get('longitude', 0)
            message_text = f"Location: {lat}, {lng}"
            message_type = "Location"
        else:
            message_text = str(message_payload)
        
        # Gupshup message ID
        gupshup_message_id = payload.get('id', '')
        
        # Clean source phone number
        clean_source = source_phone.replace('+', '') if source_phone.startswith('+') else source_phone
        
        frappe.log_error(f"Processing incoming message from {clean_source}: {message_text}", "WhatsApp Incoming")
        
        # Create incoming message document
        result = create_incoming_message_doc(
            source_phone=clean_source,
            message=message_text,
            message_type=message_type,
            media_url=media_url,
            media_type=media_type,
            gupshup_message_id=gupshup_message_id
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Error processing incoming message: {str(e)}", "WhatsApp Incoming Error")
        return {"status": "error", "message": str(e)}

def create_incoming_message_doc(source_phone, message, message_type="Text", 
                               media_url=None, media_type=None, gupshup_message_id=None):
    """Create WhatsApp Message document for incoming message"""
    try:
        # Get or create contacts
        source_contact = get_or_create_contact_simple(source_phone)
        destination_contact = get_or_create_contact_simple(GUPSHUP_CONFIG["source_number"])
        
        # Check for duplicate messages
        if gupshup_message_id:
            existing = frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id})
            if existing:
                return {"status": "duplicate", "message": "Message already exists"}
        
        # Generate message ID if not provided
        if not gupshup_message_id:
            gupshup_message_id = f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create WhatsApp Message document
        message_data = {
            "doctype": "WhatsApp Message",
            "source": source_phone,
            "message": message,
            "message_id": gupshup_message_id,
            "direction": "Incoming",
            "message_type": message_type,
            "status": "Delivered",
            "timestamp": datetime.now(),
            "content": f"Received: {message}"[:100]
        }
        
        # Add destination - use contact if exists, otherwise phone number
        if destination_contact:
            message_data["destination"] = destination_contact
        else:
            message_data["destination"] = GUPSHUP_CONFIG["source_number"]
        
        # Add optional fields
        if media_url:
            message_data["media_url"] = media_url
        if media_type:
            message_data["media_type"] = media_type
        if source_contact:
            message_data["contact"] = source_contact
        
        # Add destination_name if field exists
        try:
            message_data["destination_name"] = "Your Business"
        except:
            pass
        
        message_doc = frappe.get_doc(message_data)
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Update last message date on contact
        try:
            if source_contact:
                frappe.db.set_value("Whatsapp Contact", source_contact, "last_message_date", datetime.now())
                frappe.db.commit()
        except:
            pass
        
        frappe.log_error(f"Successfully created incoming message: {message_doc.name}", "WhatsApp Success")
        
        return {
            "status": "success", 
            "message_doc_name": message_doc.name,
            "contact": source_contact,
            "destination_contact": destination_contact,
            "message_id": gupshup_message_id,
            "phone": source_phone,
            "text": message,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating incoming message doc: {str(e)}", "WhatsApp Document Error")
        return {"status": "error", "message": str(e)}

def get_or_create_contact_simple(phone_number):
    """Get or create Whatsapp Contact with error handling"""
    try:
        # Clean phone number
        clean_phone = phone_number.replace('+', '') if phone_number.startswith('+') else phone_number
        
        # Try to find existing contact
        existing_contact = frappe.get_all(
            "Whatsapp Contact",
            filters={"phone_number": clean_phone},
            fields=["name"],
            limit=1
        )
        
        if existing_contact:
            return existing_contact[0].name
        else:
            try:
                # Determine contact name
                if clean_phone == GUPSHUP_CONFIG["source_number"]:
                    contact_name = "Your Business"
                else:
                    contact_name = f"Contact {clean_phone[-4:]}"
                
                contact_doc = frappe.get_doc({
                    "doctype": "Whatsapp Contact",
                    "phone_number": clean_phone,
                    "name1": contact_name
                })
                
                # Add opt_in_status if field exists
                if hasattr(contact_doc, 'opt_in_status'):
                    contact_doc.opt_in_status = "Opted In"
                
                contact_doc.insert(ignore_permissions=True)
                frappe.db.commit()
                
                return contact_doc.name
                
            except Exception as contact_error:
                frappe.log_error(f"Contact creation failed: {str(contact_error)}", "Contact Creation Error")
                return None
            
    except Exception as e:
        frappe.log_error(f"Error in get_or_create_contact: {str(e)}", "Contact Error")
        return None

@frappe.whitelist()
def send_test_message(destination, message):
    """Test sending message via Gupshup API"""
    try:
        # Clean destination number
        clean_destination = str(destination).replace("+", "")
        if not clean_destination.startswith('91') and len(clean_destination) == 10:
            clean_destination = '91' + clean_destination
        
        # Prepare message data for Gupshup
        message_data = {
            'type': 'text',
            'text': str(message)
        }
        
        # Prepare form data for Gupshup API
        form_data = {
            'channel': 'whatsapp',
            'source': GUPSHUP_CONFIG["source_number"],
            'destination': clean_destination,
            'message': json.dumps(message_data),
            'src.name': GUPSHUP_CONFIG["app_name"]
        }
        
        # Make API call to Gupshup
        success, response_data, error_msg = make_gupshup_api_call(form_data)
        
        # Create WhatsApp Message record
        message_id = f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Get or create contacts
        source_contact = get_or_create_contact_simple(GUPSHUP_CONFIG["source_number"])
        destination_contact = get_or_create_contact_simple(clean_destination)
        
        message_doc_data = {
            "doctype": "WhatsApp Message",
            "source": GUPSHUP_CONFIG["source_number"],
            "message": message,
            "message_id": message_id,
            "direction": "Outgoing",
            "message_type": "Text",
            "status": "Sent" if success else "Failed",
            "timestamp": datetime.now(),
            "content": f"Sent via Gupshup: {str(response_data)[:100]}"
        }
        
        # Add destination - use contact if exists, otherwise phone number
        if destination_contact:
            message_doc_data["destination"] = destination_contact
            message_doc_data["contact"] = destination_contact
        else:
            message_doc_data["destination"] = clean_destination
        
        message_doc = frappe.get_doc(message_doc_data)
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "success": success,
            "message": "Message sent successfully" if success else f"Failed to send: {error_msg}",
            "gupshup_response": response_data,
            "frappe_doc": message_doc.name,
            "message_id": message_id,
            "destination": clean_destination,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        frappe.log_error(f"Send test message error: {str(e)}", "Send Test Error")
        return {
            "success": False,
            "error": str(e)
        }

def make_gupshup_api_call(form_data):
    """Make API call to Gupshup"""
    try:
        # Encode the data
        data = urllib.parse.urlencode(form_data).encode('utf-8')
        
        # Create the request
        req = urllib.request.Request(
            GUPSHUP_CONFIG["api_endpoint"],
            data=data,
            headers={
                'apikey': GUPSHUP_CONFIG["api_key"],
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        # Make the API call
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            
        frappe.log_error(f"Gupshup API Response: {response_data}", "Gupshup API Success")
        return True, response_data, None
        
    except Exception as api_error:
        error_msg = str(api_error)
        frappe.log_error(f"Gupshup API Error: {error_msg}", "Gupshup API Error")
        return False, f"API Error: {error_msg}", error_msg

@frappe.whitelist()
def send_whatsapp_message_enhanced(destination, message, message_type="Text"):
    """Enhanced message sending for chat interface"""
    try:
        result = send_test_message(destination, message)
        
        # Return data in format expected by chat interface
        if result.get("success"):
            return {
                "success": True,
                "message_doc_name": result.get("frappe_doc"),
                "message_id": result.get("message_id"),
                "gupshup_response": result.get("gupshup_response"),
                "timestamp": result.get("timestamp")
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error")
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def process_delivery_report(data):
    """Process delivery report from Gupshup"""
    try:
        payload = data.get('payload', {})
        message_id = payload.get('gsId', '')
        event_type = payload.get('type', '')
        
        # Map Gupshup event types to our status
        status_mapping = {
            "sent": "Sent",
            "delivered": "Delivered", 
            "read": "Read",
            "failed": "Failed"
        }
        
        new_status = status_mapping.get(event_type, "Sent")
        
        # Find and update the message
        message_docs = frappe.get_all(
            "WhatsApp Message",
            filters={"message_id": message_id},
            fields=["name"],
            limit=1
        )
        
        if message_docs:
            frappe.db.set_value("WhatsApp Message", message_docs[0].name, "status", new_status)
            frappe.db.commit()
            
            frappe.log_error(f"Updated message {message_id} status to {new_status}", "WhatsApp Status Update")
            return {"status": "success", "message": f"Status updated to {new_status}"}
        else:
            return {"status": "not_found", "message": "Message not found"}
            
    except Exception as e:
        frappe.log_error(f"Error processing delivery report: {str(e)}", "WhatsApp Delivery Error")
        return {"status": "error", "message": str(e)}

@frappe.whitelist()
def test_webhook():
    """Test webhook functionality"""
    try:
        # Simulate incoming message data
        test_data = {
            "type": "message",
            "payload": {
                "id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "source": "919746574552",
                "payload": {
                    "type": "text",
                    "text": "Test incoming message - complete webhook"
                }
            }
        }
        
        result = process_incoming_message(test_data)
        return {
            "status": "success",
            "message": "Webhook test completed",
            "result": result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_recent_messages(contact_phone, limit=50):
    """Get recent messages for a contact (for real-time updates)"""
    try:
        clean_phone = contact_phone.replace('+', '') if contact_phone.startswith('+') else contact_phone
        our_number = GUPSHUP_CONFIG["source_number"]
        
        # Get messages where source or destination matches the contact
        messages = frappe.get_all(
            "WhatsApp Message",
            filters=[
                ["OR", 
                    [["source", "=", clean_phone], ["destination", "=", our_number]],
                    [["source", "=", our_number], ["destination", "=", clean_phone]]
                ]
            ],
            fields=["name", "source", "destination", "message", "direction", "message_type", 
                   "status", "timestamp", "message_id", "creation"],
            order_by="creation desc",
            limit=limit
        )
        
        return {
            "status": "success",
            "messages": messages
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting recent messages: {str(e)}", "Messages Error")
        return {
            "status": "error",
            "message": str(e)
        }

# Legacy webhook functions for compatibility
@frappe.whitelist(allow_guest=True)
def gupshup_webhook():
    """Legacy webhook function - redirects to main handler"""
    return handle_gupshup_webhook()

@frappe.whitelist(allow_guest=True)
def gupshup_opt_in_webhook():
    """Handle opt-in webhooks from Gupshup"""
    try:
        data = frappe.local.form_dict
        
        phone_number = data.get('mobile')
        opt_in_status = data.get('optin')
        
        if phone_number:
            clean_phone = phone_number.replace('+', '') if phone_number.startswith('+') else phone_number
            
            existing_contact = frappe.get_all(
                "Whatsapp Contact",
                filters={"phone_number": clean_phone},
                limit=1
            )
            
            status = "Opted In" if opt_in_status == "true" else "Opted Out"
            
            if existing_contact:
                try:
                    frappe.db.set_value("Whatsapp Contact", existing_contact[0].name, "opt_in_status", status)
                except:
                    pass
            else:
                try:
                    contact_doc = frappe.get_doc({
                        "doctype": "Whatsapp Contact",
                        "phone_number": clean_phone,
                        "name1": clean_phone
                    })
                    
                    if hasattr(contact_doc, 'opt_in_status'):
                        contact_doc.opt_in_status = status
                    
                    contact_doc.insert(ignore_permissions=True)
                except Exception as contact_error:
                    frappe.log_error(f"Opt-in contact creation error: {str(contact_error)}", "Opt-in Error")
                
            frappe.db.commit()
        
        return {"status": "success"}
        
    except Exception as e:
        frappe.log_error(str(e), "Opt-in Error")
        return {"status": "error", "message": str(e)}