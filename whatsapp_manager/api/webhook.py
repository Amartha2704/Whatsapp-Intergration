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
        # Log the request method
        frappe.log_error(f"Webhook called with method: {frappe.request.method}", "WhatsApp Webhook Debug")
        
        # Get the request data - try multiple methods
        data = None
        
        # Method 1: Try JSON data first
        if hasattr(frappe.request, 'get_json'):
            try:
                data = frappe.request.get_json(force=True)
            except:
                pass
        
        # Method 2: Try form data
        if not data:
            data = frappe.local.form_dict
        
        # Method 3: Try raw data
        if not data and hasattr(frappe.request, 'get_data'):
            try:
                raw_data = frappe.request.get_data(as_text=True)
                if raw_data:
                    data = json.loads(raw_data)
            except:
                pass
        
        # Log the received data for debugging
        frappe.log_error(f"Webhook received data: {json.dumps(data, indent=2) if data else 'No data'}", "WhatsApp Webhook Data")
        
        if not data:
            return {"status": "error", "message": "No data received"}
        
        # Check if this is a verification request (some platforms send these)
        if 'hub.challenge' in data:
            return data.get('hub.challenge')
        
        # Extract message information from webhook
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            return process_incoming_message(data)
        elif message_type == 'message-event':
            return process_delivery_report(data)
        elif message_type == 'user-event':
            return process_user_event(data)
        else:
            frappe.log_error(f"Unknown webhook type: {message_type}", "WhatsApp Webhook")
            return {"status": "success", "message": f"Ignored type: {message_type}"}
            
    except Exception as e:
        error_msg = str(e)
        frappe.log_error(f"Webhook error: {error_msg}\nData: {frappe.local.form_dict}", "WhatsApp Webhook Error")
        return {"status": "error", "message": error_msg}

def process_incoming_message(data):
    """Process incoming WhatsApp message and create it with direction='Incoming'"""
    try:
        # Extract message details from webhook format
        payload = data.get('payload', {})
        
        # Source phone number (sender) - this is who sent the message TO us
        source_phone = payload.get('source', '')
        
        # Destination should be our business number
        destination_phone = payload.get('destination', GUPSHUP_CONFIG["source_number"])
        
        # Message content
        message_payload = payload.get('payload', {})
        message_text = ""
        message_type = "Text"
        media_url = None
        media_type = None
        
        # Handle different message types from Gupshup
        msg_type = message_payload.get('type', 'text')
        
        if msg_type == 'text':
            message_text = message_payload.get('text', '')
        elif msg_type == 'image':
            message_text = message_payload.get('caption', '') or 'Image received'
            message_type = "Image"
            media_url = message_payload.get('url', '')
            media_type = "image"
        elif msg_type == 'audio':
            message_text = message_payload.get('caption', '') or 'Audio message received'
            message_type = "Audio"
            media_url = message_payload.get('url', '')
            media_type = "audio"
        elif msg_type == 'video':
            message_text = message_payload.get('caption', '') or 'Video received'
            message_type = "Video"
            media_url = message_payload.get('url', '')
            media_type = "video"
        elif msg_type == 'file' or msg_type == 'document':
            filename = message_payload.get('filename', 'document')
            message_text = f"Document received: {filename}"
            message_type = "Document"
            media_url = message_payload.get('url', '')
            media_type = "document"
        elif msg_type == 'location':
            lat = message_payload.get('latitude', 0)
            lng = message_payload.get('longitude', 0)
            message_text = f"Location shared: {lat}, {lng}"
            message_type = "Location"
        elif msg_type == 'contact':
            contact_name = message_payload.get('name', 'Contact')
            message_text = f"Contact shared: {contact_name}"
            message_type = "Contact"
        else:
            message_text = f"Unsupported message type: {msg_type}"
        
        # Gupshup message ID
        gupshup_message_id = payload.get('id', '')
        timestamp = payload.get('timestamp', '')
        
        # Clean phone numbers
        clean_source = clean_phone_number(source_phone)
        clean_destination = clean_phone_number(destination_phone)
        
        frappe.log_error(f"Processing INCOMING message from {clean_source} to {clean_destination}: {message_text}", "WhatsApp Incoming")
        
        # Create incoming message document with direction='Incoming'
        result = create_incoming_message_doc(
            source_phone=clean_source,
            destination_phone=clean_destination,
            message=message_text,
            message_type=message_type,
            media_url=media_url,
            media_type=media_type,
            gupshup_message_id=gupshup_message_id,
            timestamp=timestamp
        )
        
        return result
        
    except Exception as e:
        frappe.log_error(f"Error processing incoming message: {str(e)}", "WhatsApp Incoming Error")
        return {"status": "error", "message": str(e)}

def create_incoming_message_doc(source_phone, destination_phone, message, message_type="Text", 
                               media_url=None, media_type=None, gupshup_message_id=None, timestamp=None):
    """Create WhatsApp Message document for incoming message with direction='Incoming'"""
    try:
        # Check for duplicate messages first
        if gupshup_message_id:
            existing = frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id})
            if existing:
                frappe.log_error(f"Duplicate message ignored: {gupshup_message_id}", "WhatsApp Duplicate")
                return {"status": "duplicate", "message": "Message already exists"}
        
        # Generate message ID if not provided
        if not gupshup_message_id:
            gupshup_message_id = f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Get or create contacts
        source_contact = get_or_create_contact(source_phone)
        destination_contact = get_or_create_contact(destination_phone)
        
        # Parse timestamp
        parsed_timestamp = None
        if timestamp:
            try:
                # Gupshup usually sends timestamp in milliseconds
                if isinstance(timestamp, str):
                    timestamp = int(timestamp)
                parsed_timestamp = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1000000000000 else timestamp)
            except:
                parsed_timestamp = datetime.now()
        else:
            parsed_timestamp = datetime.now()
        
        # Create WhatsApp Message document with direction='Incoming'
        message_data = {
            "doctype": "WhatsApp Message",
            "source": source_phone,  # Phone number of sender (customer)
            "destination": destination_phone,  # Our business number
            "message": message,
            "message_id": gupshup_message_id,
            "direction": "Incoming",  # This is crucial - marks it as received message
            "message_type": message_type,
            "status": "Delivered",  # Incoming messages are automatically delivered
            "timestamp": parsed_timestamp,
            "creation": parsed_timestamp,
            "modified": parsed_timestamp
        }
        
        # Add optional fields if they exist in the doctype
        if media_url:
            message_data["media_url"] = media_url
        if media_type:
            message_data["media_type"] = media_type
        if source_contact:
            message_data["contact"] = source_contact
            
        # Try to add other fields that might exist
        try:
            message_data["content"] = f"Received: {message}"[:140]
        except:
            pass
            
        try:
            message_data["sender_name"] = get_contact_name(source_phone)
        except:
            pass
        
        # Create and insert the document
        message_doc = frappe.get_doc(message_data)
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Update last message date on sender contact
        if source_contact:
            try:
                frappe.db.set_value("Whatsapp Contact", source_contact, {
                    "last_message_date": parsed_timestamp,
                    "last_message": message[:100]
                })
                frappe.db.commit()
            except Exception as contact_update_error:
                frappe.log_error(f"Error updating contact: {str(contact_update_error)}", "Contact Update Error")
        
        frappe.log_error(f"✅ Successfully created INCOMING message: {message_doc.name} from {source_phone}", "WhatsApp Success")
        
        return {
            "status": "success", 
            "message_doc_name": message_doc.name,
            "direction": "Incoming",
            "source": source_phone,
            "destination": destination_phone,
            "message_id": gupshup_message_id,
            "message": message,
            "timestamp": parsed_timestamp.isoformat() if parsed_timestamp else None
        }
        
    except Exception as e:
        frappe.log_error(f"❌ Error creating incoming message doc: {str(e)}\nData: {locals()}", "WhatsApp Document Error")
        return {"status": "error", "message": str(e)}

def get_or_create_contact(phone_number):
    """Get or create Whatsapp Contact with better error handling"""
    try:
        clean_phone = clean_phone_number(phone_number)
        
        # Try to find existing contact
        existing_contact = frappe.get_all(
            "Whatsapp Contact",
            filters={"phone_number": clean_phone},
            fields=["name"],
            limit=1
        )
        
        if existing_contact:
            return existing_contact[0].name
        
        # Create new contact
        try:
            contact_name = get_contact_name(clean_phone)
            
            contact_doc = frappe.get_doc({
                "doctype": "Whatsapp Contact",
                "phone_number": clean_phone,
                "name1": contact_name
            })
            
            # Add opt_in_status if field exists
            try:
                contact_doc.opt_in_status = "Opted In"
            except:
                pass
            
            # Add other optional fields
            try:
                if clean_phone == GUPSHUP_CONFIG["source_number"]:
                    contact_doc.is_business = 1
            except:
                pass
                
            contact_doc.insert(ignore_permissions=True)
            frappe.db.commit()
            
            frappe.log_error(f"Created new contact: {contact_doc.name} for {clean_phone}", "Contact Created")
            return contact_doc.name
            
        except Exception as contact_error:
            frappe.log_error(f"Contact creation failed for {clean_phone}: {str(contact_error)}", "Contact Creation Error")
            return None
            
    except Exception as e:
        frappe.log_error(f"Error in get_or_create_contact for {phone_number}: {str(e)}", "Contact Error")
        return None

def clean_phone_number(phone_number):
    """Clean and standardize phone number"""
    if not phone_number:
        return phone_number
        
    # Remove spaces, dashes, parentheses
    clean = str(phone_number).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Remove + if present
    if clean.startswith('+'):
        clean = clean[1:]
    
    # Add 91 if it's a 10-digit Indian number
    if len(clean) == 10 and clean.isdigit():
        clean = '91' + clean
    
    return clean

def get_contact_name(phone_number):
    """Generate a contact name from phone number"""
    clean_phone = clean_phone_number(phone_number)
    
    if clean_phone == GUPSHUP_CONFIG["source_number"]:
        return "Your Business"
    else:
        return f"Contact {clean_phone[-4:]}"

def process_delivery_report(data):
    """Process delivery report from Gupshup"""
    try:
        payload = data.get('payload', {})
        message_id = payload.get('gsId', '')
        event_type = payload.get('type', '').lower()
        timestamp = payload.get('timestamp', '')
        
        # Map Gupshup event types to our status
        status_mapping = {
            "sent": "Sent",
            "delivered": "Delivered", 
            "read": "Read",
            "failed": "Failed",
            "enroute": "Sent"
        }
        
        new_status = status_mapping.get(event_type, "Sent")
        
        # Find and update the message
        message_docs = frappe.get_all(
            "WhatsApp Message",
            filters={"message_id": message_id},
            fields=["name", "status"],
            limit=1
        )
        
        if message_docs:
            message_doc = message_docs[0]
            old_status = message_doc.status
            
            # Only update if status is actually changing
            if old_status != new_status:
                frappe.db.set_value("WhatsApp Message", message_doc.name, "status", new_status)
                frappe.db.commit()
                
                frappe.log_error(f"📋 Updated message {message_id} status: {old_status} → {new_status}", "WhatsApp Status Update")
            
            return {"status": "success", "message": f"Status updated to {new_status}"}
        else:
            frappe.log_error(f"❌ Delivery report for unknown message: {message_id}", "WhatsApp Unknown Message")
            return {"status": "not_found", "message": "Message not found"}
            
    except Exception as e:
        frappe.log_error(f"Error processing delivery report: {str(e)}", "WhatsApp Delivery Error")
        return {"status": "error", "message": str(e)}

def process_user_event(data):
    """Process user events like opt-in/opt-out"""
    try:
        payload = data.get('payload', {})
        phone_number = payload.get('phone', '')
        event_type = payload.get('type', '')
        
        if phone_number and event_type in ['opt-in', 'opt-out']:
            clean_phone = clean_phone_number(phone_number)
            status = "Opted In" if event_type == 'opt-in' else "Opted Out"
            
            # Update or create contact
            contact = get_or_create_contact(clean_phone)
            if contact:
                try:
                    frappe.db.set_value("Whatsapp Contact", contact, "opt_in_status", status)
                    frappe.db.commit()
                except:
                    pass
            
            frappe.log_error(f"User event: {phone_number} {event_type}", "WhatsApp User Event")
        
        return {"status": "success", "message": "User event processed"}
        
    except Exception as e:
        frappe.log_error(f"Error processing user event: {str(e)}", "WhatsApp User Event Error")
        return {"status": "error", "message": str(e)}

# Enhanced sending functions for the chat interface

@frappe.whitelist()
def send_whatsapp_message(destination, message, message_id=None):
    """Send WhatsApp message via Gupshup API and create outgoing record"""
    try:
        # Clean destination number
        clean_destination = clean_phone_number(destination)
        
        # Generate message ID if not provided
        if not message_id:
            message_id = f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
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
        
        # Create WhatsApp Message record with direction='Outgoing'
        message_doc_data = {
            "doctype": "WhatsApp Message",
            "source": GUPSHUP_CONFIG["source_number"],  # Our business number
            "destination": clean_destination,  # Customer's number
            "message": message,
            "message_id": message_id,
            "direction": "Outgoing",  # This marks it as sent message
            "message_type": "Text",
            "status": "Sent" if success else "Failed",
            "timestamp": datetime.now()
        }
        
        # Add contact if exists
        destination_contact = get_or_create_contact(clean_destination)
        if destination_contact:
            message_doc_data["contact"] = destination_contact
        
        message_doc = frappe.get_doc(message_doc_data)
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.log_error(f"📤 Created OUTGOING message: {message_doc.name} to {clean_destination}", "WhatsApp Sent")
        
        return {
            "success": success,
            "message": "Message sent successfully" if success else f"Failed to send: {error_msg}",
            "gupshup_response": response_data,
            "frappe_doc": message_doc.name,
            "message_id": message_id,
            "destination": clean_destination,
            "direction": "Outgoing",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        frappe.log_error(f"Send message error: {str(e)}", "Send Message Error")
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
def test_webhook():
    """Test webhook functionality by simulating incoming message"""
    try:
        # Simulate incoming message data from Gupshup
        test_data = {
            "type": "message",
            "payload": {
                "id": f"test_incoming_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "source": "919876543210",  # Test customer number
                "destination": GUPSHUP_CONFIG["source_number"],  # Our business number
                "timestamp": str(int(datetime.now().timestamp() * 1000)),
                "payload": {
                    "type": "text",
                    "text": "This is a test incoming message to verify webhook functionality"
                }
            }
        }
        
        result = process_incoming_message(test_data)
        
        return {
            "status": "success",
            "message": "Webhook test completed - incoming message created",
            "result": result,
            "test_data": test_data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist()
def get_webhook_logs(limit=20):
    """Get recent webhook logs for debugging"""
    try:
        logs = frappe.get_all(
            "Error Log",
            filters=[
                ["error", "like", "%WhatsApp%"]
            ],
            fields=["name", "error", "creation", "method"],
            order_by="creation desc",
            limit=limit
        )
        
        return {
            "status": "success",
            "logs": logs
        }
        
    except Exception as e:
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
def simple_test():
    """Ultra-simple test endpoint"""
    return {
        "status": "success", 
        "message": "Webhook endpoint is working!", 
        "timestamp": str(datetime.now()),
        "method": frappe.request.method,
        "headers": dict(frappe.request.headers) if hasattr(frappe.request, 'headers') else {},
        "form_data": frappe.local.form_dict
    }