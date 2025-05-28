# chat.py - Fixed WhatsApp Integration

import requests
import frappe
from frappe import _
import json
from datetime import datetime, timedelta
import urllib.parse
import urllib.request
from frappe.utils import now

@frappe.whitelist()
def send_whatsapp_message(destination, message, message_id=None, message_type="Text"):
    """Send text messages via WhatsApp using Gupshup API and log in WhatsApp Message Doctype"""
    try:
        # Clean phone number
        clean_destination = str(destination).replace("+", "").strip()
        if not clean_destination.startswith('91') and len(clean_destination) == 10:
            clean_destination = '91' + clean_destination
        
        # Get or create WhatsApp contact
        contact_result = get_contact_by_phone(clean_destination)
        if contact_result.get("status") != "success":
            return {
                "success": False,
                "message": "Failed to get/create contact",
                "error": "Contact creation failed"
            }

        contact = contact_result.get("contact")
        contact_name = contact.get("name")
        
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
        
        # Make API request to Gupshup
        success, response_data, error_msg = make_gupshup_request(form_data)

        # Parse Gupshup response
        gupshup_message_id = None
        if success and response_data:
            try:
                response_json = json.loads(response_data)
                gupshup_message_id = response_json.get('messageId')
            except Exception as parse_error:
                frappe.log_error(str(parse_error), "Gupshup Response Parse Error")

        # Use existing message_id or generate new one
        final_message_id = gupshup_message_id or message_id or frappe.generate_hash(length=15)

        # Create WhatsApp Message Doc with error handling
        doc_name = None
        try:
            # Get the WhatsApp Message doctype to understand its fields
            doctype_meta = frappe.get_meta("WhatsApp Message")
            
            # Prepare document data with only valid fields
            doc_data = {
                "doctype": "WhatsApp Message"
            }
            
            # Add fields that exist in the doctype
            field_mapping = {
                "contact": contact_name,
                "source": "919746574552", 
                "destination": clean_destination,  # Use phone number instead of contact name
                "destination_name": clean_destination,
                "message": str(message),
                "direction": "Outgoing",
                "message_id": final_message_id,
                "message_type": message_type,
                "status": "Sent" if success else "Failed",
                "timestamp": datetime.now(),
                "content": f"Sent: {message}"[:100] if len(str(message)) > 100 else f"Sent: {message}",
                "media_url": None,
                "media_type": None
            }
            
            # Only add fields that exist in the doctype
            for field_name, field_value in field_mapping.items():
                if any(field.fieldname == field_name for field in doctype_meta.fields):
                    doc_data[field_name] = field_value
            
            # Create document
            message_doc = frappe.get_doc(doc_data)
            
            # Insert without validation to avoid field validation issues
            message_doc.flags.ignore_validate = True
            message_doc.flags.ignore_mandatory = True
            message_doc.insert(ignore_permissions=True, ignore_mandatory=True)
            frappe.db.commit()
            
            doc_name = message_doc.name

            # Update contact's last message date if field exists
            try:
                contact_meta = frappe.get_meta("Whatsapp Contact")
                if any(field.fieldname == "last_message_date" for field in contact_meta.fields):
                    frappe.db.set_value("Whatsapp Contact", contact_name, "last_message_date", datetime.now())
                    frappe.db.commit()
            except Exception as update_error:
                frappe.log_error(str(update_error), "Failed to update contact last message date")

        except Exception as doc_error:
            frappe.log_error(f"Failed to create WhatsApp Message doc: {str(doc_error)}", "WhatsApp Doc Creation Error")
            # Don't return error here, as the message was still sent successfully

        return {
            "success": success,
            "message": "Message sent and logged successfully" if (success and doc_name) else 
                      "Message sent successfully" if success else f"Failed to send: {error_msg}",
            "gupshup_response": response_data,
            "frappe_doc": doc_name,
            "message_id": final_message_id,
            "contact": contact_name,
            "doc_created": bool(doc_name)
        }

    except Exception as e:
        frappe.log_error(f"WhatsApp Message Error: {str(e)}", "WhatsApp Integration Error")
        return {
            "success": False, 
            "error": str(e),
            "message": f"Integration error: {str(e)}"
        }

@frappe.whitelist(allow_guest=True)
def get_contact_by_phone(phone_number):
    """Get or create contact by phone number"""
    try:
        # Clean phone number - remove + prefix to match existing format
        clean_phone = str(phone_number).lstrip('+') if str(phone_number).startswith('+') else str(phone_number)
            
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
            contact_doc.flags.ignore_validate = True
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
        frappe.log_error(f"Gupshup API Error: {error_msg}", "WhatsApp API Error")
        return False, f"API Error: {error_msg}", error_msg

@frappe.whitelist()
def get_contacts():
    """Get all WhatsApp contacts with basic info"""
    try:
        contacts = frappe.get_all(
            "Whatsapp Contact",
            fields=["name", "phone_number", "name1", "last_message_date", "opt_in_status"],
            order_by="creation desc"  # Changed from last_message_date to creation to avoid field errors
        )
       
        # Get last message for each contact
        for contact in contacts:
            try:
                last_message = frappe.get_all(
                    "WhatsApp Message",
                    filters={"contact": contact.name},
                    fields=["message", "timestamp", "direction"],
                    order_by="timestamp desc",
                    limit=1
                )
               
                if last_message:
                    contact["last_message"] = last_message[0].message
                    contact["last_message_time"] = last_message[0].timestamp
                else:
                    contact["last_message"] = ""
                    contact["last_message_time"] = None
               
                # Count unread messages (messages from last 7 days)
                unread_count = frappe.db.count(
                    "WhatsApp Message",
                    filters={
                        "contact": contact.name,
                        "direction": "Incoming",
                        "timestamp": [">", datetime.now() - timedelta(days=7)]
                    }
                )
                contact["unread_count"] = unread_count
                
            except Exception as contact_error:
                contact["last_message"] = ""
                contact["unread_count"] = 0
                frappe.log_error(f"Error processing contact {contact.name}: {str(contact_error)}")
       
        return {
            "status": "success",
            "contacts": contacts
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting contacts: {str(e)}", "WhatsApp Get Contacts Error")
        return {
            "status": "error",
            "message": str(e),
            "contacts": []
        }

@frappe.whitelist()
def get_messages(contact):
    """Get messages for a specific contact"""
    try:
        messages = frappe.get_all(
            "WhatsApp Message",
            filters={"contact": contact},
            fields=["name", "direction", "message_type", "message",
                    "media_url", "media_type", "status", "timestamp"],
            order_by="timestamp asc"
        )
       
        return {
            "status": "success",
            "messages": messages
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting messages for contact {contact}: {str(e)}", "WhatsApp Get Messages Error")
        return {
            "status": "error",
            "message": str(e),
            "messages": []
        }

@frappe.whitelist(allow_guest=True)
def handle_incoming_message(phone_number, message, message_type="Text", media_url=None, media_type=None, gupshup_message_id=None):
    """Handle incoming WhatsApp messages from Gupshup webhook"""
    try:
        # Prevent duplicates using Gupshup message ID
        if gupshup_message_id and frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id}):
            return {"status": "duplicate", "message": "Message already exists"}

        # Clean phone number
        clean_phone = str(phone_number).lstrip('+') if str(phone_number).startswith('+') else str(phone_number)
        
        # Get or create contact
        contact_result = get_contact_by_phone(phone_number)
        if contact_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Failed to get/create contact"
            }
        
        contact_name = contact_result["contact"]["name"]
        contact_name1 = contact_result["contact"]["name1"]
        
        # Get the WhatsApp Message doctype to understand its fields
        doctype_meta = frappe.get_meta("WhatsApp Message")
        
        # Prepare document data with only valid fields
        doc_data = {
            "doctype": "WhatsApp Message"
        }
        
        # Add fields that exist in the doctype
        field_mapping = {
            "contact": contact_name,
            "source": clean_phone,
            "destination": "919746574552",
            "destination_name": "SmartSchool",
            "message": str(message),
            "direction": "Incoming",
            "message_id": gupshup_message_id or f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            "message_type": message_type,
            "status": "Delivered",
            "timestamp": datetime.now(),
            "content": f"Received: {message}"[:100] if len(str(message)) > 100 else f"Received: {message}",
            "media_url": media_url,
            "media_type": media_type
        }
        
        # Only add fields that exist in the doctype
        for field_name, field_value in field_mapping.items():
            if any(field.fieldname == field_name for field in doctype_meta.fields):
                doc_data[field_name] = field_value
        
        # Create incoming message document
        message_doc = frappe.get_doc(doc_data)
        message_doc.flags.ignore_validate = True
        message_doc.flags.ignore_mandatory = True
        message_doc.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.commit()
        
        # Update last message date on contact if field exists
        try:
            contact_meta = frappe.get_meta("Whatsapp Contact")
            if any(field.fieldname == "last_message_date" for field in contact_meta.fields):
                frappe.db.set_value("Whatsapp Contact", contact_name, "last_message_date", datetime.now())
                frappe.db.commit()
        except Exception as update_error:
            frappe.log_error(str(update_error), "Failed to update contact last message date")
        
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
def test_gupshup_connection():
    """Test Gupshup API connection"""
    try:
        form_data = {
            'channel': 'whatsapp',
            'source': '919746574552',
            'destination': '919746574552',  # Send to self
            'message': json.dumps({
                'type': 'text',
                'text': 'Connection test from Frappe - Integration working!'
            }),
            'src.name': 'smartschool'
        }
        
        success, response_data, error_msg = make_gupshup_request(form_data)
        
        return {
            "success": success,
            "response": response_data,
            "message": "Connection test successful!" if success else f"Connection failed: {error_msg}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Configuration error"
        }

@frappe.whitelist()
def debug_whatsapp_doctype():
    """Debug function to check WhatsApp Message doctype fields"""
    try:
        doctype_meta = frappe.get_meta("WhatsApp Message")
        fields = []
        
        for field in doctype_meta.fields:
            fields.append({
                "fieldname": field.fieldname,
                "fieldtype": field.fieldtype,
                "label": field.label,
                "reqd": field.reqd
            })
        
        return {
            "status": "success",
            "doctype": "WhatsApp Message",
            "fields": fields
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }