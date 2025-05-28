# import frappe
# from frappe import _
# import json
# from datetime import datetime, timedelta



# @frappe.whitelist()
# def create_whatsapp_message(message, message_id, sent=1):
#     """Create a new WhatsApp Message document"""
#     try:
#         doc = frappe.get_doc({
#             "doctype": "WhatsApp Message",
#             "message": message,
#             "message_id": message_id,
#             "sent": int(sent),
#             "timestamp": frappe.utils.now(),
#         })
#         doc.insert()
#         frappe.db.commit()
        
#         return {
#             "success": True,
#             "message": "WhatsApp message created successfully",
#             "name": doc.name
#         }
#     except Exception as e:
#         frappe.log_error(f"WhatsApp Message Creation Error: {str(e)}")
#         return {
#             "success": False,
#             "error": str(e)
#         }
# @frappe.whitelist()
# def get_contacts():
#     """Get all WhatsApp contacts with basic info"""
#     contacts = frappe.get_all(
#         "Whatsapp Contact",
#         fields=["name", "phone_number", "name1", "last_message_date", "opt_in_status"],
#         order_by="last_message_date desc"
#     )
   
#     # Get last message for each contact
#     for contact in contacts:
#         last_message = frappe.get_all(
#             "WhatsApp Message",
#             filters={"contact": contact.name},
#             fields=["message", "timestamp", "direction"],
#             order_by="timestamp desc",
#             limit=1
#         )
       
#         if last_message:
#             contact["last_message"] = last_message[0].message
#         else:
#             contact["last_message"] = ""
       
#         # Count unread messages
#         unread_count = frappe.db.count(
#             "WhatsApp Message",
#             filters={
#                 "contact": contact.name,
#                 "direction": "Incoming",
#                 "timestamp": [">", datetime.now() - timedelta(days=7)]
#             }
#         )
       
#         contact["unread_count"] = unread_count
   
#     return contacts

# @frappe.whitelist()
# def get_messages(contact):
#     """Get messages for a specific contact"""
#     messages = frappe.get_all(
#         "WhatsApp Message",
#         filters={"contact": contact},
#         fields=["name", "direction", "message_type", "message",
#                 "media_url", "media_type", "status", "timestamp"],
#         order_by="timestamp asc"
#     )
   
#     return messages

# def create_whatsapp_message_doc(contact, message, message_type="Text", direction="Outgoing", 
#                                media_url=None, media_type=None, status="Sent", gupshup_message_id=None):
#     """Create a WhatsApp Message document"""
#     try:
#         # Clean phone number - remove + prefix to match existing format
#         if contact.startswith("+"):
#             clean_phone = contact.lstrip('+')
#         else:
#             clean_phone = contact
        
#         # Get contact phone number if contact is a name
#         if not clean_phone.isdigit():
#             try:
#                 contact_doc = frappe.get_doc("Whatsapp Contact", contact)
#                 phone_number = contact_doc.phone_number
#                 contact_name = contact
#             except:
#                 # If contact doesn't exist, treat as phone number
#                 phone_number = clean_phone
#                 contact_name = None
#         else:
#             phone_number = clean_phone
#             contact_name = None
        
#         # Try to find existing contact by phone number
#         if not contact_name:
#             existing_contact = frappe.get_all(
#                 "Whatsapp Contact",
#                 filters={"phone_number": phone_number},
#                 limit=1
#             )
#             if existing_contact:
#                 contact_name = existing_contact[0].name
#             else:
#                 # Create new contact if doesn't exist
#                 contact_doc = frappe.get_doc({
#                     "doctype": "Whatsapp Contact",
#                     "phone_number": phone_number,
#                     "name1": phone_number,
#                     "opt_in_status": "Opted In"
#                 })
#                 contact_doc.insert(ignore_permissions=True)
#                 contact_name = contact_doc.name
        
#         # Set source and destination based on direction
#         if direction == "Incoming":
#             source_number = phone_number
#             destination_contact = contact_name  # Your business contact
#         else:
#             source_number = "Your Business"  # Your business number
#             destination_contact = contact_name
        
#         # Map status to valid options
#         status_mapping = {
#             "Received": "Delivered",  # Map Received to Delivered
#             "Sent": "Sent",
#             "Delivered": "Delivered", 
#             "Read": "Read",
#             "Failed": "Failed",
#             "submitted": "submitted"
#         }
#         valid_status = status_mapping.get(status, "Sent")  # Default to "Sent"
        
#         # Create WhatsApp Message document with all required fields
#         message_doc = frappe.get_doc({
#             "doctype": "WhatsApp Message",
#             "contact": contact_name,                    # Field 2: Contact (Link) - REQUIRED
#             "source": source_number,                    # Field 3: source (Data) - REQUIRED  
#             "destination": destination_contact,         # Field 4: destination (Link) - REQUIRED
#             "destination_name": phone_number,           # Field 5: destination_name (Data)
#             "direction": direction,                     # Field 6: direction (Select)
#             "message_id": gupshup_message_id,          # Field 8: message_id (Data)
#             "message_type": message_type,              # Field 9: message_type (Select)
#             "status": valid_status,                    # Field 10: status (Select) - using valid option
#             "timestamp": datetime.now(),               # Field 11: timestamp (Datetime)
#             "message": message,                        # Field 13: message (Text)
#             "content": f"Message: {message}"[:100],    # Field 15: content (Data)
#             "media_url": media_url,                    # Field 17: media_url (Data)
#             "media_type": media_type,                  # Field 18: media_type (Data)
#         })
        
#         message_doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         # Update last message date on contact if that field exists
#         try:
#             frappe.db.set_value("Whatsapp Contact", contact_name, "last_message_date", datetime.now())
#             frappe.db.commit()
#         except:
#             pass  # Field might not exist
        
#         return message_doc.name
        
#     except Exception as e:
#         frappe.log_error(str(e), "Message Creation Error")
#         return None

# @frappe.whitelist()
# def handle_incoming_message(phone_number, message, message_type, media_url=None, media_type=None, gupshup_message_id=None):
#     # Prevent duplicates using Gupshup message ID
#     if gupshup_message_id and frappe.db.exists("WhatsApp Message", {"gupshup_message_id": gupshup_message_id}):
#         return {"status": "duplicate", "message": "Already exists"}

#     doc = frappe.get_doc({
#         "doctype": "WhatsApp Message",
#         "phone_number": phone_number,
#         "message": message,
#         "message_type": message_type,
#         "media_url": media_url,
#         "media_type": media_type,
#         "direction": "Incoming",
#         "gupshup_message_id": gupshup_message_id
#     })
#     doc.insert(ignore_permissions=True)
#     frappe.db.commit()
    
#     return {"status": "success", "message_id": doc.name}

# # def handle_incoming_message(phone_number, message, message_type="Text", media_url=None, 
# #                            media_type=None, gupshup_message_id=None):
# #     """Handle incoming WhatsApp messages from Gupshup webhook"""
# #     try:
# #         # Create the incoming message record using the working create function
# #         message_doc_name = create_whatsapp_message_doc(
# #             contact=phone_number,
# #             message=message,
# #             message_type=message_type,
# #             direction="Incoming",
# #             media_url=media_url,
# #             media_type=media_type,
# #             status="Delivered",  # Use valid status for incoming messages
# #             gupshup_message_id=gupshup_message_id
# #         )
        
# #         if message_doc_name:
# #             return {"status": "success", "message_doc_name": message_doc_name}
# #         else:
# #             return {"status": "error", "message": "Failed to create message document"}
        
# #     except Exception as e:
# #         frappe.log_error(str(e), "Incoming Message Error")
# #         return {"status": "error", "message": str(e)}

# @frappe.whitelist()
# def update_message_status(gupshup_message_id, status):
#     """Update message status based on Gupshup delivery reports"""
#     try:
#         # Map status to valid options
#         status_mapping = {
#             "Enroute": "Sent",
#             "Delivered": "Delivered",
#             "Read": "Read", 
#             "Failed": "Failed",
#             "Sent": "Sent"
#         }
#         valid_status = status_mapping.get(status, "Sent")
        
#         # Find message by Gupshup message ID
#         message_doc = frappe.get_all(
#             "WhatsApp Message",
#             filters={"message_id": gupshup_message_id},  # Using your message_id field
#             limit=1
#         )
        
#         if message_doc:
#             frappe.db.set_value("WhatsApp Message", message_doc[0].name, "status", valid_status)
#             frappe.db.commit()
#             return {"status": "success", "message": "Status updated"}
#         else:
#             return {"status": "error", "message": "Message not found"}
            
#     except Exception as e:
#         frappe.log_error(str(e), "Status Update Error")
#         return {"status": "error", "message": str(e)}

# @frappe.whitelist()
# def send_message_api(contact, message, message_type="Text", media_url=None):
#     """API endpoint to send a WhatsApp message (simplified version)"""
#     try:
#         # For now, just create the message document without sending via Gupshup
#         # You can add the actual Gupshup sending logic later
        
#         message_doc_name = create_whatsapp_message_doc(
#             contact=contact,
#             message=message,
#             message_type=message_type,
#             direction="Outgoing",
#             media_url=media_url,
#             status="Sent",
#             gupshup_message_id=f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
#         )
        
#         return {
#             "status": "submitted",
#             "message": "Message created successfully",
#             "message_doc_name": message_doc_name
#         }
        
#     except Exception as e:
#         frappe.log_error(f"Error in send_message_api: {str(e)}", "WhatsApp Send Message Error")
#         return {"status": "error", "message": str(e)}

# @frappe.whitelist()
# def get_contact_by_phone(phone_number):
#     """Get or create contact by phone number"""
#     try:
#         # Clean phone number - remove + prefix to match existing format
#         clean_phone = phone_number.lstrip('+')
            
#         # Try to find existing contact
#         existing_contact = frappe.get_all(
#             "Whatsapp Contact",
#             filters={"phone_number": clean_phone},
#             fields=["name", "name1", "opt_in_status"],
#             limit=1
#         )
        
#         if existing_contact:
#             return existing_contact[0]
#         else:
#             # Create new contact with clean phone number (no + prefix)
#             contact_doc = frappe.get_doc({
#                 "doctype": "Whatsapp Contact",
#                 "phone_number": clean_phone,
#                 "name1": clean_phone,
#                 "opt_in_status": "Opted In"
#             })
#             contact_doc.insert(ignore_permissions=True)
#             frappe.db.commit()
            
#             return {
#                 "name": contact_doc.name,
#                 "name1": contact_doc.name1,
#                 "opt_in_status": contact_doc.opt_in_status
#             }
            
#     except Exception as e:
#         frappe.log_error(f"Error getting/creating contact: {str(e)}", "WhatsApp Contact Error")
#         return None


import requests
import frappe
from frappe import _
import json
from datetime import datetime, timedelta

@frappe.whitelist()
def create_whatsapp_message(message, message_id, sent=1):
    """Create a new WhatsApp Message document"""
    try:
        doc = frappe.get_doc({
            "doctype": "WhatsApp Message",
            "message": message,
            "message_id": message_id,
            "sent": int(sent),
            "timestamp": frappe.utils.now(),
        })
        doc.insert()
        frappe.db.commit()
        
        return {
            "success": True,
            "message": "WhatsApp message created successfully",
            "name": doc.name
        }
    except Exception as e:
        frappe.log_error(f"WhatsApp Message Creation Error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@frappe.whitelist()
def get_contacts():
    """Get all WhatsApp contacts with basic info"""
    contacts = frappe.get_all(
        "Whatsapp Contact",
        fields=["name", "phone_number", "name1", "last_message_date", "opt_in_status"],
        order_by="last_message_date desc"
    )
   
    # Get last message for each contact
    for contact in contacts:
        last_message = frappe.get_all(
            "WhatsApp Message",
            filters={"contact": contact.name},
            fields=["message", "timestamp", "direction"],
            order_by="timestamp desc",
            limit=1
        )
       
        if last_message:
            contact["last_message"] = last_message[0].message
        else:
            contact["last_message"] = ""
       
        # Count unread messages
        unread_count = frappe.db.count(
            "WhatsApp Message",
            filters={
                "contact": contact.name,
                "direction": "Incoming",
                "timestamp": [">", datetime.now() - timedelta(days=7)]
            }
        )
       
        contact["unread_count"] = unread_count
   
    return contacts

@frappe.whitelist()
def get_messages(contact):
    """Get messages for a specific contact"""
    messages = frappe.get_all(
        "WhatsApp Message",
        filters={"contact": contact},
        fields=["name", "direction", "message_type", "message",
                "media_url", "media_type", "status", "timestamp"],
        order_by="timestamp asc"
    )
   
    return messages

@frappe.whitelist(allow_guest=True)
def get_contact_by_phone(phone_number):
    """Get or create contact by phone number"""
    try:
        # Clean phone number - remove + prefix to match existing format
        clean_phone = phone_number.lstrip('+') if phone_number.startswith('+') else phone_number
            
        # Try to find existing contact
        existing_contact = frappe.get_all(
            "Whatsapp Contact",
            filters={"phone_number": clean_phone},
            fields=["name", "name1", "opt_in_status"],
            limit=1
        )
        
        if existing_contact:
            return {
                "status": "success",
                "contact": existing_contact[0]
            }
        else:
            # Create new contact with clean phone number (no + prefix)
            contact_doc = frappe.get_doc({
                "doctype": "Whatsapp Contact",
                "phone_number": clean_phone,
                "name1": clean_phone,
                "opt_in_status": "Opted In"
            })
            contact_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            return {
                "status": "success",
                "contact": {
                    "name": contact_doc.name,
                    "name1": contact_doc.name1,
                    "opt_in_status": contact_doc.opt_in_status
                }
            }
            
    except Exception as e:
        frappe.log_error(f"Error getting/creating contact: {str(e)}", "WhatsApp Contact Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist(allow_guest=True) 
def send_message_api(contact, message, message_type="Text", media_url=None):
    """API endpoint to send a WhatsApp message"""
    try:
        # Clean phone number - remove + prefix to match existing format
        if contact.startswith("+"):
            clean_phone = contact.lstrip('+')
        else:
            clean_phone = contact
        
        # Get or create contact first
        contact_result = get_contact_by_phone(contact)
        if contact_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Failed to get/create contact"
            }
        
        contact_name = contact_result["contact"]["name"]
        
        # Generate unique message ID
        message_id = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create WhatsApp Message document with proper field mapping
        message_doc = frappe.get_doc({
            "doctype": "WhatsApp Message",
            # Required fields according to your doctype
            "contact": contact_name,                    # Link to Whatsapp Contact
            "source": "919746574552",                  # Data field (required)
            "destination": contact_name,                # Link to Whatsapp Contact (required)
            "message": message,                         # Text field (required)
            
            # Optional fields
            "destination_name": contact_result["contact"]["name1"],            # Data field
            "direction": "Outgoing",                    # Select field
            "message_id": message_id,                   # Data field
            "message_type": message_type,               # Select field
            "status": "Sent",                          # Select field
            "timestamp": datetime.now(),                # Datetime field
            "content": f"Sent: {message}"[:100],       # Data field (log)
            "media_url": media_url,                     # Data field
            "media_type": None                          # Data field
        })
        
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Update last message date on contact if that field exists
        try:
            frappe.db.set_value("Whatsapp Contact", contact_name, "last_message_date", datetime.now())
            frappe.db.commit()
        except:
            pass  # Field might not exist
        
        return {
            "status": "success",
            "message": "Message created successfully",
            "message_doc_name": message_doc.name,
            "message_id": message_id
        }
        
    except Exception as e:
        frappe.log_error(f"Error in send_message_api: {str(e)}", "WhatsApp Send Message Error")
        return {
            "status": "error", 
            "message": str(e)
        }

@frappe.whitelist()
def handle_incoming_message(phone_number, message, message_type="Text", media_url=None, media_type=None, gupshup_message_id=None):
    """Handle incoming WhatsApp messages from Gupshup webhook"""
    try:
        # Prevent duplicates using Gupshup message ID
        if gupshup_message_id and frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id}):
            return {"status": "duplicate", "message": "Message already exists"}

        # Clean phone number
        clean_phone = phone_number.lstrip('+') if phone_number.startswith('+') else phone_number
        
        # Get or create contact
        contact_result = get_contact_by_phone(phone_number)
        if contact_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Failed to get/create contact"
            }
        
        contact_name = contact_result["contact"]["name"]
        
        # Create incoming message document
        message_doc = frappe.get_doc({
            "doctype": "WhatsApp Message",
            # Required fields
            "contact": contact_name,                    # Link to Whatsapp Contact
            "source": clean_phone,                      # Data field (required)
            "destination": "919074704695",             # Link/Data field (required) 
            "message": message,                         # Text field (required)
            
            # Optional fields
            "destination_name": "Amartha",        # Data field
            "direction": "Outgoing",                    # Select field
            "message_id": gupshup_message_id or f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "message_type": message_type,               # Select field
            "status": "Sent",                      # Select field
            "timestamp": datetime.now(),                # Datetime field
            "content": f"Received: {message}"[:100],    # Data field (log)
            "media_url": media_url,                     # Data field
            "media_type": media_type                    # Data field
        })
        
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Update last message date on contact
        try:
            frappe.db.set_value("Whatsapp Contact", contact_name, "last_message_date", datetime.now())
            frappe.db.commit()
        except:
            pass
        
        return {
            "status": "success", 
            "message_doc_name": message_doc.name
        }
        
    except Exception as e:
        frappe.log_error(f"Incoming Message Error: {str(e)}", "WhatsApp Incoming Message Error")
        return {
            "status": "error", 
            "message": str(e)
        }

@frappe.whitelist()
def update_message_status(gupshup_message_id, status):
    """Update message status based on Gupshup delivery reports"""
    try:
        # Map status to valid options
        status_mapping = {
            "Enroute": "Sent",
            "Delivered": "Delivered",
            "Read": "Read", 
            "Failed": "Failed",
            "Sent": "Sent"
        }
        valid_status = status_mapping.get(status, "Sent")
        
        # Find message by Gupshup message ID
        message_doc = frappe.get_all(
            "WhatsApp Message",
            filters={"message_id": gupshup_message_id},
            limit=1
        )
        
        if message_doc:
            frappe.db.set_value("WhatsApp Message", message_doc[0].name, "status", valid_status)
            frappe.db.commit()
            return {"status": "success", "message": "Status updated"}
        else:
            return {"status": "error", "message": "Message not found"}
            
    except Exception as e:
        frappe.log_error(str(e), "Status Update Error")
        return {"status": "error", "message": str(e)}
    


    # your_custom_app/api.py


# File: whatsapp_manager/api/chat.py

@frappe.whitelist()
def send_whatsapp_message(doc_name):
    """
    Send WhatsApp message via Gupshup API
    Called from client script or automatically via hooks
    """
    try:
        # Get the document
        doc = frappe.get_doc("WhatsApp Message", doc_name)
        
        # Validate document
        validate_message_doc(doc)
        
        # Check if already sent
        if doc.get('gupshup_sent'):
            return {
                "success": False,
                "message": "Message already sent via Gupshup",
                "status": "already_sent"
            }
        
        # Prepare message data
        message_data = prepare_message_data(doc)
        
        # Send to Gupshup
        response = send_to_gupshup(message_data)
        
        # Update document based on response
        if response.get('success'):
            update_success_status(doc, response['data'])
            return {
                "success": True,
                "message": "WhatsApp message sent successfully",
                "gupshup_response": response['data']
            }
        else:
            update_error_status(doc, response.get('error', 'Unknown error'))
            return {
                "success": False,
                "message": f"Failed to send: {response.get('error', 'Unknown error')}",
                "gupshup_response": response.get('data', {})
            }
            
    except Exception as e:
        frappe.log_error(f"WhatsApp Send Error: {str(e)}", "WhatsApp Integration")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
# Enhanced WhatsApp Message Server Scripts
# Create these as separate Server Scripts in Frappe

# Script 1: Text Messages
import frappe
import json
import urllib.parse
import urllib.request
from frappe.utils import now

@frappe.whitelist()
def send_whatsapp_message(destination, message, message_id=None, message_type="Text"):
    """Send text messages via WhatsApp using Gupshup API"""
    try:
        # Clean phone number
        clean_destination = str(destination).replace("+", "")
        if not clean_destination.startswith('91') and len(clean_destination) == 10:
            clean_destination = '91' + clean_destination
        
        # Prepare form data for Gupshup
        form_data = {
            'channel': 'whatsapp',
            'source': '919746574552',
            'destination': clean_destination,
            'message': json.dumps({
                'type': 'text',
                'text': str(message)
            }),
            'src.name': 'smartschool'
        }
        
        # Make API call
        success, response_data, error_msg = make_gupshup_request(form_data)
        
        # Generate message ID if not provided
        if not message_id:
            message_id = frappe.generate_hash(length=15)
        
        # Create WhatsApp Message document
        doc_name = create_whatsapp_message_doc(
            clean_destination, message, message_id, message_type, success, response_data
        )
        
        return {
            "success": success,
            "message": f"Message sent successfully" if success else f"Failed to send: {error_msg}",
            "gupshup_response": response_data,
            "frappe_doc": doc_name,
            "message_id": message_id
        }
        
    except Exception as e:
        frappe.log_error(f"WhatsApp Message Error: {str(e)}")
        return {"success": False, "error": str(e)}

# Script 2: File Messages (Images, Audio, Video, Documents)
# API Method: send_whatsapp_file
@frappe.whitelist()
def send_whatsapp_file(destination, message, message_id=None, message_type="Document", extra_data=None):
    """Send file attachments via WhatsApp using Gupshup API"""
    try:
        # Clean phone number
        clean_destination = str(destination).replace("+", "")
        if not clean_destination.startswith('91') and len(clean_destination) == 10:
            clean_destination = '91' + clean_destination
        
        # Parse extra data
        if extra_data and isinstance(extra_data, str):
            extra_data = json.loads(extra_data)
        
        file_url = extra_data.get('file_url', '') if extra_data else ''
        file_name = extra_data.get('file_name', 'file') if extra_data else 'file'
        caption = extra_data.get('caption', '') if extra_data else ''
        
        # Get the full file URL
        if file_url and not file_url.startswith('http'):
            file_url = frappe.utils.get_url() + file_url
        
        # Prepare message based on file type
        if message_type == 'Image':
            message_data = {
                'type': 'image',
                'originalUrl': file_url,
                'previewUrl': file_url,
                'caption': caption
            }
        elif message_type == 'Video':
            message_data = {
                'type': 'video',
                'url': file_url,
                'caption': caption
            }
        elif message_type == 'Audio':
            message_data = {
                'type': 'audio',
                'url': file_url
            }
        else:  # Document
            message_data = {
                'type': 'file',
                'url': file_url,
                'filename': file_name,
                'caption': caption
            }
        
        # Prepare form data for Gupshup
        form_data = {
            'channel': 'whatsapp',
            'source': '919746574552',
            'destination': clean_destination,
            'message': json.dumps(message_data),
            'src.name': 'smartschool'
        }
        
        # Make API call
        success, response_data, error_msg = make_gupshup_request(form_data)
        
        # Generate message ID if not provided
        if not message_id:
            message_id = frappe.generate_hash(length=15)
        
        # Create WhatsApp Message document
        doc_name = create_whatsapp_message_doc(
            clean_destination, caption or f"📎 {file_name}", message_id, message_type, success, response_data, file_url
        )
        
        return {
            "success": success,
            "message": f"File sent successfully" if success else f"Failed to send file: {error_msg}",
            "gupshup_response": response_data,
            "frappe_doc": doc_name,
            "message_id": message_id,
            "file_url": file_url
        }
        
    except Exception as e:
        frappe.log_error(f"WhatsApp File Error: {str(e)}")
        return {"success": False, "error": str(e)}

# Script 3: Location Messages
# API Method: send_whatsapp_location
@frappe.whitelist()
def send_whatsapp_location(destination, message, message_id=None, message_type="Location", extra_data=None):
    """Send location messages via WhatsApp using Gupshup API"""
    try:
        # Clean phone number
        clean_destination = str(destination).replace("+", "")
        if not clean_destination.startswith('91') and len(clean_destination) == 10:
            clean_destination = '91' + clean_destination
        
        # Parse extra data
        if extra_data and isinstance(extra_data, str):
            extra_data = json.loads(extra_data)
        
        latitude = extra_data.get('latitude', 0) if extra_data else 0
        longitude = extra_data.get('longitude', 0) if extra_data else 0
        name = extra_data.get('name', 'Location') if extra_data else 'Location'
        
        # Prepare location message for Gupshup
        message_data = {
            'type': 'location',
            'latitude': latitude,
            'longitude': longitude,
            'name': name,
            'address': f"Lat: {latitude}, Long: {longitude}"
        }
        
        # Prepare form data for Gupshup
        form_data = {
            'channel': 'whatsapp',
            'source': '919746574552',
            'destination': clean_destination,
            'message': json.dumps(message_data),
            'src.name': 'smartschool'
        }
        
        # Make API call
        success, response_data, error_msg = make_gupshup_request(form_data)
        
        # Generate message ID if not provided
        if not message_id:
            message_id = frappe.generate_hash(length=15)
        
        # Create WhatsApp Message document
        doc_name = create_whatsapp_message_doc(
            clean_destination, f"📍 {name}", message_id, message_type, success, response_data
        )
        
        return {
            "success": success,
            "message": f"Location sent successfully" if success else f"Failed to send location: {error_msg}",
            "gupshup_response": response_data,
            "frappe_doc": doc_name,
            "message_id": message_id,
            "location": {"latitude": latitude, "longitude": longitude, "name": name}
        }
        
    except Exception as e:
        frappe.log_error(f"WhatsApp Location Error: {str(e)}")
        return {"success": False, "error": str(e)}

# Helper Functions
def make_gupshup_request(form_data):
    """Make request to Gupshup API"""
    try:
        # Encode the data
        data = urllib.parse.urlencode(form_data).encode('utf-8')
        
        # Create the request
        req = urllib.request.Request(
            'https://api.gupshup.io/sm/api/v1/msg',
            data=data,
            headers={
                'apikey': 'qpk4f7vilyb0ef8oeawrflbsap055zmt',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        # Make the API call
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            
        return True, response_data, None
        
    except Exception as api_error:
        error_msg = str(api_error)
        return False, f"API Error: {error_msg}", error_msg

def create_whatsapp_message_doc(destination, message, message_id, message_type, success, response_data, file_url=None):
    """Create WhatsApp Message document in Frappe"""
    try:
        doc_data = {
            "doctype": "WhatsApp Message",
            "source": "919746574552",
            "destination": destination,
            "message": str(message),
            "message_id": message_id,
            "direction": "Outgoing",
            "message_type": message_type,
            "status": "Sent" if success else "Failed",
            "timestamp": now(),
        }
        
        # Add file URL if provided
        if file_url and hasattr(frappe.get_doc("WhatsApp Message"), 'file_url'):
            doc_data['file_url'] = file_url
            
        whatsapp_doc = frappe.get_doc(doc_data)
        whatsapp_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return whatsapp_doc.name
        
    except Exception as doc_error:
        frappe.log_error(f"Failed to create WhatsApp Message doc: {str(doc_error)}")
        return None

# Script 4: Connection Test
# API Method: test_gupshup_connection
@frappe.whitelist()
def test_gupshup_connection():
    """Test Gupshup API connection"""
    try:
        form_data = {
            'channel': 'whatsapp',
            'source': '919746574552',
            'destination': '919746574552',  # Send to self
            'message': json.dumps({
                'type': 'text',
                'text': 'Connection test from Frappe - All message types supported!'
            }),
            'src.name': 'smartschool'
        }
        
        success, response_data, error_msg = make_gupshup_request(form_data)
        
        return {
            "success": success,
            "response": response_data,
            "message": "Connection test successful - All message types ready!" if success else f"Connection failed: {error_msg}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Configuration error"
        }