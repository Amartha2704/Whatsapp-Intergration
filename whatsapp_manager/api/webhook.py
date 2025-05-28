# # import frappe
# # from frappe import _
# # import json
# # import urllib.parse
# # import urllib.request
# # from datetime import datetime

# # # Gupshup Configuration
# # GUPSHUP_CONFIG = {
# #     "api_key": "qpk4f7vilyb0ef8oeawrflbsap055zmt",
# #     "source_number": "919746574552",
# #     "api_endpoint": "https://api.gupshup.io/sm/api/v1/msg",
# #     "app_name": "smartschool"
# # }

# # @frappe.whitelist(allow_guest=True)
# # def handle_gupshup_webhook():
# #     """
# #     Main webhook endpoint to receive incoming WhatsApp messages from Gupshup
# #     URL: https://smartschool.prismaticsoft.com/api/method/whatsapp_manager.api.webhook.handle_gupshup_webhook
# #     """
# #     try:
# #         # Log the request method
# #         frappe.log_error(f"Webhook called with method: {frappe.request.method}", "WhatsApp Webhook Debug")
        
# #         # Get the request data - try multiple methods
# #         data = None
        
# #         # Method 1: Try JSON data first
# #         if hasattr(frappe.request, 'get_json'):
# #             try:
# #                 data = frappe.request.get_json(force=True)
# #             except:
# #                 pass
        
# #         # Method 2: Try form data
# #         if not data:
# #             data = frappe.local.form_dict
        
# #         # Method 3: Try raw data
# #         if not data and hasattr(frappe.request, 'get_data'):
# #             try:
# #                 raw_data = frappe.request.get_data(as_text=True)
# #                 if raw_data:
# #                     data = json.loads(raw_data)
# #             except:
# #                 pass
        
# #         # Log the received data for debugging
# #         frappe.log_error(f"Webhook received data: {json.dumps(data, indent=2) if data else 'No data'}", "WhatsApp Webhook Data")
        
# #         if not data:
# #             return {"status": "error", "message": "No data received"}
        
# #         # Check if this is a verification request (some platforms send these)
# #         if 'hub.challenge' in data:
# #             return data.get('hub.challenge')
        
# #         # Extract message information from webhook
# #         message_type = data.get('type', 'message')
        
# #         if message_type == 'message':
# #             return process_incoming_message(data)
# #         elif message_type == 'message-event':
# #             return process_delivery_report(data)
# #         elif message_type == 'user-event':
# #             return process_user_event(data)
# #         else:
# #             frappe.log_error(f"Unknown webhook type: {message_type}", "WhatsApp Webhook")
# #             return {"status": "success", "message": f"Ignored type: {message_type}"}
            
# #     except Exception as e:
# #         error_msg = str(e)
# #         frappe.log_error(f"Webhook error: {error_msg}\nData: {frappe.local.form_dict}", "WhatsApp Webhook Error")
# #         return {"status": "error", "message": error_msg}

# # def process_incoming_message(data):
# #     """Process incoming WhatsApp message and create it with direction='Incoming'"""
# #     try:
# #         # Extract message details from webhook format
# #         payload = data.get('payload', {})
        
# #         # Source phone number (sender) - this is who sent the message TO us
# #         source_phone = payload.get('source', '')
        
# #         # Destination should be our business number
# #         destination_phone = payload.get('destination', GUPSHUP_CONFIG["source_number"])
        
# #         # Message content
# #         message_payload = payload.get('payload', {})
# #         message_text = ""
# #         message_type = "Text"
# #         media_url = None
# #         media_type = None
        
# #         # Handle different message types from Gupshup
# #         msg_type = message_payload.get('type', 'text')
        
# #         if msg_type == 'text':
# #             message_text = message_payload.get('text', '')
# #         elif msg_type == 'image':
# #             message_text = message_payload.get('caption', '') or 'Image received'
# #             message_type = "Image"
# #             media_url = message_payload.get('url', '')
# #             media_type = "image"
# #         elif msg_type == 'audio':
# #             message_text = message_payload.get('caption', '') or 'Audio message received'
# #             message_type = "Audio"
# #             media_url = message_payload.get('url', '')
# #             media_type = "audio"
# #         elif msg_type == 'video':
# #             message_text = message_payload.get('caption', '') or 'Video received'
# #             message_type = "Video"
# #             media_url = message_payload.get('url', '')
# #             media_type = "video"
# #         elif msg_type == 'file' or msg_type == 'document':
# #             filename = message_payload.get('filename', 'document')
# #             message_text = f"Document received: {filename}"
# #             message_type = "Document"
# #             media_url = message_payload.get('url', '')
# #             media_type = "document"
# #         elif msg_type == 'location':
# #             lat = message_payload.get('latitude', 0)
# #             lng = message_payload.get('longitude', 0)
# #             message_text = f"Location shared: {lat}, {lng}"
# #             message_type = "Location"
# #         elif msg_type == 'contact':
# #             contact_name = message_payload.get('name', 'Contact')
# #             message_text = f"Contact shared: {contact_name}"
# #             message_type = "Contact"
# #         else:
# #             message_text = f"Unsupported message type: {msg_type}"
        
# #         # Gupshup message ID
# #         gupshup_message_id = payload.get('id', '')
# #         timestamp = payload.get('timestamp', '')
        
# #         # Clean phone numbers
# #         clean_source = clean_phone_number(source_phone)
# #         clean_destination = clean_phone_number(destination_phone)
        
# #         frappe.log_error(f"Processing INCOMING message from {clean_source} to {clean_destination}: {message_text}", "WhatsApp Incoming")
        
# #         # Create incoming message document with direction='Incoming'
# #         result = create_incoming_message_doc(
# #             source_phone=clean_source,
# #             destination_phone=clean_destination,
# #             message=message_text,
# #             message_type=message_type,
# #             media_url=media_url,
# #             media_type=media_type,
# #             gupshup_message_id=gupshup_message_id,
# #             timestamp=timestamp
# #         )
        
# #         return result
        
# #     except Exception as e:
# #         frappe.log_error(f"Error processing incoming message: {str(e)}", "WhatsApp Incoming Error")
# #         return {"status": "error", "message": str(e)}

# # def create_incoming_message_doc(source_phone, destination_phone, message, message_type="Text", 
# #                                media_url=None, media_type=None, gupshup_message_id=None, timestamp=None):
# #     """Create WhatsApp Message document for incoming message with direction='Incoming'"""
# #     try:
# #         # Check for duplicate messages first
# #         if gupshup_message_id:
# #             existing = frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id})
# #             if existing:
# #                 frappe.log_error(f"Duplicate message ignored: {gupshup_message_id}", "WhatsApp Duplicate")
# #                 return {"status": "duplicate", "message": "Message already exists"}
        
# #         # Generate message ID if not provided
# #         if not gupshup_message_id:
# #             gupshup_message_id = f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
# #         # Get or create contacts
# #         source_contact = get_or_create_contact(source_phone)
# #         destination_contact = get_or_create_contact(destination_phone)
        
# #         # Parse timestamp
# #         parsed_timestamp = None
# #         if timestamp:
# #             try:
# #                 # Gupshup usually sends timestamp in milliseconds
# #                 if isinstance(timestamp, str):
# #                     timestamp = int(timestamp)
# #                 parsed_timestamp = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1000000000000 else timestamp)
# #             except:
# #                 parsed_timestamp = datetime.now()
# #         else:
# #             parsed_timestamp = datetime.now()
        
# #         # Create WhatsApp Message document with direction='Incoming'
# #         message_data = {
# #             "doctype": "WhatsApp Message",
# #             "source": source_phone,  # Phone number of sender (customer)
# #             "destination": destination_phone,  # Our business number
# #             "message": message,
# #             "message_id": gupshup_message_id,
# #             "direction": "Incoming",  # This is crucial - marks it as received message
# #             "message_type": message_type,
# #             "status": "Delivered",  # Incoming messages are automatically delivered
# #             "timestamp": parsed_timestamp,
# #             "creation": parsed_timestamp,
# #             "modified": parsed_timestamp
# #         }
        
# #         # Add optional fields if they exist in the doctype
# #         if media_url:
# #             message_data["media_url"] = media_url
# #         if media_type:
# #             message_data["media_type"] = media_type
# #         if source_contact:
# #             message_data["contact"] = source_contact
            
# #         # Try to add other fields that might exist
# #         try:
# #             message_data["content"] = f"Received: {message}"[:140]
# #         except:
# #             pass
            
# #         try:
# #             message_data["sender_name"] = get_contact_name(source_phone)
# #         except:
# #             pass
        
# #         # Create and insert the document
# #         message_doc = frappe.get_doc(message_data)
# #         message_doc.insert(ignore_permissions=True)
# #         frappe.db.commit()
        
# #         # Update last message date on sender contact
# #         if source_contact:
# #             try:
# #                 frappe.db.set_value("Whatsapp Contact", source_contact, {
# #                     "last_message_date": parsed_timestamp,
# #                     "last_message": message[:100]
# #                 })
# #                 frappe.db.commit()
# #             except Exception as contact_update_error:
# #                 frappe.log_error(f"Error updating contact: {str(contact_update_error)}", "Contact Update Error")
        
# #         frappe.log_error(f"✅ Successfully created INCOMING message: {message_doc.name} from {source_phone}", "WhatsApp Success")
        
# #         return {
# #             "status": "success", 
# #             "message_doc_name": message_doc.name,
# #             "direction": "Incoming",
# #             "source": source_phone,
# #             "destination": destination_phone,
# #             "message_id": gupshup_message_id,
# #             "message": message,
# #             "timestamp": parsed_timestamp.isoformat() if parsed_timestamp else None
# #         }
        
# #     except Exception as e:
# #         frappe.log_error(f"❌ Error creating incoming message doc: {str(e)}\nData: {locals()}", "WhatsApp Document Error")
# #         return {"status": "error", "message": str(e)}

# # def get_or_create_contact(phone_number):
# #     """Get or create Whatsapp Contact with better error handling"""
# #     try:
# #         clean_phone = clean_phone_number(phone_number)
        
# #         # Try to find existing contact
# #         existing_contact = frappe.get_all(
# #             "Whatsapp Contact",
# #             filters={"phone_number": clean_phone},
# #             fields=["name"],
# #             limit=1
# #         )
        
# #         if existing_contact:
# #             return existing_contact[0].name
        
# #         # Create new contact
# #         try:
# #             contact_name = get_contact_name(clean_phone)
            
# #             contact_doc = frappe.get_doc({
# #                 "doctype": "Whatsapp Contact",
# #                 "phone_number": clean_phone,
# #                 "name1": contact_name
# #             })
            
# #             # Add opt_in_status if field exists
# #             try:
# #                 contact_doc.opt_in_status = "Opted In"
# #             except:
# #                 pass
            
# #             # Add other optional fields
# #             try:
# #                 if clean_phone == GUPSHUP_CONFIG["source_number"]:
# #                     contact_doc.is_business = 1
# #             except:
# #                 pass
                
# #             contact_doc.insert(ignore_permissions=True)
# #             frappe.db.commit()
            
# #             frappe.log_error(f"Created new contact: {contact_doc.name} for {clean_phone}", "Contact Created")
# #             return contact_doc.name
            
# #         except Exception as contact_error:
# #             frappe.log_error(f"Contact creation failed for {clean_phone}: {str(contact_error)}", "Contact Creation Error")
# #             return None
            
# #     except Exception as e:
# #         frappe.log_error(f"Error in get_or_create_contact for {phone_number}: {str(e)}", "Contact Error")
# #         return None

# # def clean_phone_number(phone_number):
# #     """Clean and standardize phone number"""
# #     if not phone_number:
# #         return phone_number
        
# #     # Remove spaces, dashes, parentheses
# #     clean = str(phone_number).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
# #     # Remove + if present
# #     if clean.startswith('+'):
# #         clean = clean[1:]
    
# #     # Add 91 if it's a 10-digit Indian number
# #     if len(clean) == 10 and clean.isdigit():
# #         clean = '91' + clean
    
# #     return clean

# # def get_contact_name(phone_number):
# #     """Generate a contact name from phone number"""
# #     clean_phone = clean_phone_number(phone_number)
    
# #     if clean_phone == GUPSHUP_CONFIG["source_number"]:
# #         return "Your Business"
# #     else:
# #         return f"Contact {clean_phone[-4:]}"

# # def process_delivery_report(data):
# #     """Process delivery report from Gupshup"""
# #     try:
# #         payload = data.get('payload', {})
# #         message_id = payload.get('gsId', '')
# #         event_type = payload.get('type', '').lower()
# #         timestamp = payload.get('timestamp', '')
        
# #         # Map Gupshup event types to our status
# #         status_mapping = {
# #             "sent": "Sent",
# #             "delivered": "Delivered", 
# #             "read": "Read",
# #             "failed": "Failed",
# #             "enroute": "Sent"
# #         }
        
# #         new_status = status_mapping.get(event_type, "Sent")
        
# #         # Find and update the message
# #         message_docs = frappe.get_all(
# #             "WhatsApp Message",
# #             filters={"message_id": message_id},
# #             fields=["name", "status"],
# #             limit=1
# #         )
        
# #         if message_docs:
# #             message_doc = message_docs[0]
# #             old_status = message_doc.status
            
# #             # Only update if status is actually changing
# #             if old_status != new_status:
# #                 frappe.db.set_value("WhatsApp Message", message_doc.name, "status", new_status)
# #                 frappe.db.commit()
                
# #                 frappe.log_error(f"📋 Updated message {message_id} status: {old_status} → {new_status}", "WhatsApp Status Update")
            
# #             return {"status": "success", "message": f"Status updated to {new_status}"}
# #         else:
# #             frappe.log_error(f"❌ Delivery report for unknown message: {message_id}", "WhatsApp Unknown Message")
# #             return {"status": "not_found", "message": "Message not found"}
            
# #     except Exception as e:
# #         frappe.log_error(f"Error processing delivery report: {str(e)}", "WhatsApp Delivery Error")
# #         return {"status": "error", "message": str(e)}

# # def process_user_event(data):
# #     """Process user events like opt-in/opt-out"""
# #     try:
# #         payload = data.get('payload', {})
# #         phone_number = payload.get('phone', '')
# #         event_type = payload.get('type', '')
        
# #         if phone_number and event_type in ['opt-in', 'opt-out']:
# #             clean_phone = clean_phone_number(phone_number)
# #             status = "Opted In" if event_type == 'opt-in' else "Opted Out"
            
# #             # Update or create contact
# #             contact = get_or_create_contact(clean_phone)
# #             if contact:
# #                 try:
# #                     frappe.db.set_value("Whatsapp Contact", contact, "opt_in_status", status)
# #                     frappe.db.commit()
# #                 except:
# #                     pass
            
# #             frappe.log_error(f"User event: {phone_number} {event_type}", "WhatsApp User Event")
        
# #         return {"status": "success", "message": "User event processed"}
        
# #     except Exception as e:
# #         frappe.log_error(f"Error processing user event: {str(e)}", "WhatsApp User Event Error")
# #         return {"status": "error", "message": str(e)}

# # # Enhanced sending functions for the chat interface

# # @frappe.whitelist()
# # def send_whatsapp_message(destination, message, message_id=None):
# #     """Send WhatsApp message via Gupshup API and create outgoing record"""
# #     try:
# #         # Clean destination number
# #         clean_destination = clean_phone_number(destination)
        
# #         # Generate message ID if not provided
# #         if not message_id:
# #             message_id = f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
# #         # Prepare message data for Gupshup
# #         message_data = {
# #             'type': 'text',
# #             'text': str(message)
# #         }
        
# #         # Prepare form data for Gupshup API
# #         form_data = {
# #             'channel': 'whatsapp',
# #             'source': GUPSHUP_CONFIG["source_number"],
# #             'destination': clean_destination,
# #             'message': json.dumps(message_data),
# #             'src.name': GUPSHUP_CONFIG["app_name"]
# #         }
        
# #         # Make API call to Gupshup
# #         success, response_data, error_msg = make_gupshup_api_call(form_data)
        
# #         # Create WhatsApp Message record with direction='Outgoing'
# #         message_doc_data = {
# #             "doctype": "WhatsApp Message",
# #             "source": GUPSHUP_CONFIG["source_number"],  # Our business number
# #             "destination": clean_destination,  # Customer's number
# #             "message": message,
# #             "message_id": message_id,
# #             "direction": "Outgoing",  # This marks it as sent message
# #             "message_type": "Text",
# #             "status": "Sent" if success else "Failed",
# #             "timestamp": datetime.now()
# #         }
        
# #         # Add contact if exists
# #         destination_contact = get_or_create_contact(clean_destination)
# #         if destination_contact:
# #             message_doc_data["contact"] = destination_contact
        
# #         message_doc = frappe.get_doc(message_doc_data)
# #         message_doc.insert(ignore_permissions=True)
# #         frappe.db.commit()
        
# #         frappe.log_error(f"📤 Created OUTGOING message: {message_doc.name} to {clean_destination}", "WhatsApp Sent")
        
# #         return {
# #             "success": success,
# #             "message": "Message sent successfully" if success else f"Failed to send: {error_msg}",
# #             "gupshup_response": response_data,
# #             "frappe_doc": message_doc.name,
# #             "message_id": message_id,
# #             "destination": clean_destination,
# #             "direction": "Outgoing",
# #             "timestamp": datetime.now().isoformat()
# #         }
        
# #     except Exception as e:
# #         frappe.log_error(f"Send message error: {str(e)}", "Send Message Error")
# #         return {
# #             "success": False,
# #             "error": str(e)
# #         }

# # def make_gupshup_api_call(form_data):
# #     """Make API call to Gupshup"""
# #     try:
# #         # Encode the data
# #         data = urllib.parse.urlencode(form_data).encode('utf-8')
        
# #         # Create the request
# #         req = urllib.request.Request(
# #             GUPSHUP_CONFIG["api_endpoint"],
# #             data=data,
# #             headers={
# #                 'apikey': GUPSHUP_CONFIG["api_key"],
# #                 'Content-Type': 'application/x-www-form-urlencoded'
# #             }
# #         )
        
# #         # Make the API call
# #         with urllib.request.urlopen(req, timeout=30) as response:
# #             response_data = response.read().decode('utf-8')
            
# #         frappe.log_error(f"Gupshup API Response: {response_data}", "Gupshup API Success")
# #         return True, response_data, None
        
# #     except Exception as api_error:
# #         error_msg = str(api_error)
# #         frappe.log_error(f"Gupshup API Error: {error_msg}", "Gupshup API Error")
# #         return False, f"API Error: {error_msg}", error_msg

# # @frappe.whitelist()
# # def test_webhook():
# #     """Test webhook functionality by simulating incoming message"""
# #     try:
# #         # Simulate incoming message data from Gupshup
# #         test_data = {
# #             "type": "message",
# #             "payload": {
# #                 "id": f"test_incoming_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
# #                 "source": "919876543210",  # Test customer number
# #                 "destination": GUPSHUP_CONFIG["source_number"],  # Our business number
# #                 "timestamp": str(int(datetime.now().timestamp() * 1000)),
# #                 "payload": {
# #                     "type": "text",
# #                     "text": "This is a test incoming message to verify webhook functionality"
# #                 }
# #             }
# #         }
        
# #         result = process_incoming_message(test_data)
        
# #         return {
# #             "status": "success",
# #             "message": "Webhook test completed - incoming message created",
# #             "result": result,
# #             "test_data": test_data
# #         }
        
# #     except Exception as e:
# #         return {
# #             "status": "error",
# #             "message": str(e)
# #         }

# # @frappe.whitelist()
# # def get_webhook_logs(limit=20):
# #     """Get recent webhook logs for debugging"""
# #     try:
# #         logs = frappe.get_all(
# #             "Error Log",
# #             filters=[
# #                 ["error", "like", "%WhatsApp%"]
# #             ],
# #             fields=["name", "error", "creation", "method"],
# #             order_by="creation desc",
# #             limit=limit
# #         )
        
# #         return {
# #             "status": "success",
# #             "logs": logs
# #         }
        
# #     except Exception as e:
# #         return {
# #             "status": "error",
# #             "message": str(e)
# #         }

# # # Legacy webhook functions for compatibility
# # @frappe.whitelist(allow_guest=True)
# # def gupshup_webhook():
# #     """Legacy webhook function - redirects to main handler"""
# #     return handle_gupshup_webhook()

# # @frappe.whitelist(allow_guest=True)
# # def simple_test():
# #     """Ultra-simple test endpoint"""
# #     return {
# #         "status": "success", 
# #         "message": "Webhook endpoint is working!", 
# #         "timestamp": str(datetime.now()),
# #         "method": frappe.request.method,
# #         "headers": dict(frappe.request.headers) if hasattr(frappe.request, 'headers') else {},
# #         "form_data": frappe.local.form_dict
# #     }

# # @frappe.whitelist()
# # def get_recent_messages(contact_phone, limit=50):
# #     """Get recent messages for a contact (for real-time updates)"""
# #     try:
# #         # Input validation
# #         if not contact_phone:
# #             return {
# #                 "status": "error",
# #                 "message": "Contact phone number is required"
# #             }
        
# #         # Ensure contact_phone is a string
# #         contact_phone = str(contact_phone).strip()
        
# #         # Clean phone number - remove + prefix if present
# #         clean_phone = contact_phone.replace('+', '') if contact_phone.startswith('+') else contact_phone
        
# #         # Validate that we have GUPSHUP_CONFIG
# #         if not GUPSHUP_CONFIG or not GUPSHUP_CONFIG.get("source_number"):
# #             return {
# #                 "status": "error",
# #                 "message": "WhatsApp configuration not found"
# #             }
            
# #         our_number = str(GUPSHUP_CONFIG["source_number"]).strip()
        
# #         # Validate limit parameter
# #         try:
# #             limit = int(limit)
# #             if limit <= 0 or limit > 1000:  # Set reasonable bounds
# #                 limit = 50
# #         except (ValueError, TypeError):
# #             limit = 50
       
# #         # Get messages where source or destination matches the contact
# #         # Method 1: Get incoming messages (from contact to us)
# #         incoming_messages = frappe.get_all(
# #             "WhatsApp Message",
# #             filters={
# #                 "source": clean_phone,
# #                 "destination": our_number
# #             },
# #             fields=[
# #                 "name", "source", "destination", "message", "direction", 
# #                 "message_type", "status", "timestamp", "message_id", 
# #                 "creation", "modified"
# #             ],
# #             order_by="creation desc",
# #             limit=limit
# #         )
        
# #         # Method 2: Get outgoing messages (from us to contact)
# #         outgoing_messages = frappe.get_all(
# #             "WhatsApp Message",
# #             filters={
# #                 "source": our_number,
# #                 "destination": clean_phone
# #             },
# #             fields=[
# #                 "name", "source", "destination", "message", "direction", 
# #                 "message_type", "status", "timestamp", "message_id", 
# #                 "creation", "modified"
# #             ],
# #             order_by="creation desc",
# #             limit=limit
# #         )
        
# #         # Combine and sort messages
# #         messages = incoming_messages + outgoing_messages
# #         messages.sort(key=lambda x: x.get('creation'), reverse=True)
# #         messages = messages[:limit]  # Apply limit after sorting
        
# #         # Alternative Method using raw SQL (if the above doesn't work well):
# #         # messages = frappe.db.sql("""
# #         #     SELECT name, source, destination, message, direction, message_type, 
# #         #            status, timestamp, message_id, creation, modified
# #         #     FROM `tabWhatsApp Message`
# #         #     WHERE (source = %s AND destination = %s) 
# #         #        OR (source = %s AND destination = %s)
# #         #     ORDER BY creation DESC
# #         #     LIMIT %s
# #         # """, (clean_phone, our_number, our_number, clean_phone, limit), as_dict=True)
        
# #         # Format timestamps for better frontend handling
# #         for message in messages:
# #             if message.get('timestamp'):
# #                 # Convert timestamp to ISO format if needed
# #                 message['formatted_timestamp'] = frappe.utils.get_datetime(message['timestamp']).isoformat()
# #             if message.get('creation'):
# #                 message['formatted_creation'] = frappe.utils.get_datetime(message['creation']).isoformat()
       
# #         return {
# #             "status": "success",
# #             "messages": messages,
# #             "contact_phone": clean_phone,
# #             "total_count": len(messages)
# #         }
       
# #     except frappe.DoesNotExistError:
# #         return {
# #             "status": "error",
# #             "message": "WhatsApp Message doctype not found"
# #         }
# #     except frappe.PermissionError:
# #         return {
# #             "status": "error", 
# #             "message": "Insufficient permissions to access messages"
# #         }
# #     except Exception as e:
# #         frappe.log_error(
# #             message=f"Error getting recent messages for {contact_phone}: {str(e)}", 
# #             title="WhatsApp Messages Error"
# #         )
# #         return {
# #             "status": "error",
# #             "message": "An error occurred while fetching messages"
# #         }


# # @frappe.whitelist()
# # def get_contact_info(contact_phone):
# #     """Get contact information along with recent messages"""
# #     try:
# #         if not contact_phone:
# #             return {"status": "error", "message": "Contact phone required"}
            
# #         contact_phone = str(contact_phone).strip()
# #         clean_phone = contact_phone.replace('+', '') if contact_phone.startswith('+') else contact_phone
        
# #         # Try to find contact in the system
# #         contact_info = None
# #         try:
# #             # Look for contact by phone number
# #             contacts = frappe.get_all(
# #                 "Contact",
# #                 filters={
# #                     "phone": ["like", f"%{clean_phone}%"]
# #                 },
# #                 fields=["name", "first_name", "last_name", "phone", "mobile_no"],
# #                 limit=1
# #             )
# #             if contacts:
# #                 contact_info = contacts[0]
# #         except:
# #             pass  # Contact not found, continue without it
        
# #         # Get recent messages
# #         messages_result = get_recent_messages(contact_phone, limit=20)
        
# #         return {
# #             "status": "success",
# #             "contact_info": contact_info,
# #             "messages": messages_result.get("messages", []),
# #             "phone": clean_phone
# #         }
        
# #     except Exception as e:
# #         frappe.log_error(f"Error getting contact info: {str(e)}", "Contact Info Error")
# #         return {
# #             "status": "error",
# #             "message": str(e)
# #         }

# # import frappe
# # from frappe import _
# # import json
# # import urllib.parse
# # import urllib.request
# # from datetime import datetime

# # # Gupshup Configuration
# # GUPSHUP_CONFIG = {
# #     "api_key": "qpk4f7vilyb0ef8oeawrflbsap055zmt",
# #     "source_number": "919746574552",
# #     "api_endpoint": "https://api.gupshup.io/sm/api/v1/msg",
# #     "app_name": "smartschool"
# # }

# # @frappe.whitelist(allow_guest=True)
# # def handle_gupshup_webhook():
# #     """
# #     Main webhook endpoint to receive incoming WhatsApp messages from Gupshup
# #     URL: https://smartschool.prismaticsoft.com/api/method/whatsapp_manager.api.webhook.handle_gupshup_webhook
# #     """
# #     try:
# #         # Log the request method for debugging
# #         frappe.log_error(f"Webhook called with method: {frappe.request.method}", "WhatsApp Webhook Debug")
        
# #         # Get the request data - try multiple methods
# #         data = None
        
# #         # Method 1: Try JSON data first
# #         if hasattr(frappe.request, 'get_json'):
# #             try:
# #                 data = frappe.request.get_json(force=True)
# #             except:
# #                 pass
        
# #         # Method 2: Try form data
# #         if not data:
# #             data = frappe.local.form_dict
        
# #         # Method 3: Try raw data
# #         if not data and hasattr(frappe.request, 'get_data'):
# #             try:
# #                 raw_data = frappe.request.get_data(as_text=True)
# #                 if raw_data:
# #                     data = json.loads(raw_data)
# #             except:
# #                 pass
        
# #         # Log the received data for debugging (truncated to avoid 140 char limit)
# #         data_preview = str(data)[:100] + "..." if data and len(str(data)) > 100 else str(data)
# #         frappe.log_error(f"Webhook data preview: {data_preview}", "WhatsApp Webhook Data")
        
# #         if not data:
# #             return {"status": "error", "message": "No data received"}
        
# #         # Check if this is a verification request (some platforms send these)
# #         if 'hub.challenge' in data:
# #             return data.get('hub.challenge')
        
# #         # Extract message information from webhook
# #         message_type = data.get('type', 'message')
        
# #         if message_type == 'message':
# #             return process_incoming_message_enhanced(data)
# #         elif message_type == 'message-event':
# #             return process_delivery_report(data)
# #         elif message_type == 'user-event':
# #             return process_user_event(data)
# #         else:
# #             frappe.log_error(f"Unknown webhook type: {message_type}", "WhatsApp Webhook")
# #             return {"status": "success", "message": f"Ignored type: {message_type}"}
            
# #     except Exception as e:
# #         error_msg = str(e)
# #         frappe.log_error(f"Webhook error: {error_msg}", "WhatsApp Webhook Error")
# #         return {"status": "error", "message": error_msg}

# # def process_incoming_message_enhanced(data):
# #     """Enhanced processing for incoming WhatsApp messages"""
# #     try:
# #         # Extract message details from webhook format
# #         payload = data.get('payload', {})
        
# #         # Source phone number (sender) - this is who sent the message TO us
# #         source_phone = payload.get('source', '')
        
# #         # Destination should be our business number
# #         destination_phone = payload.get('destination', GUPSHUP_CONFIG["source_number"])
        
# #         # Message content
# #         message_payload = payload.get('payload', {})
# #         message_text = ""
# #         message_type = "Text"
        
# #         # Handle different message types from Gupshup
# #         msg_type = message_payload.get('type', 'text')
        
# #         if msg_type == 'text':
# #             message_text = message_payload.get('text', '').strip()
# #         elif msg_type == 'image':
# #             message_text = message_payload.get('caption', '') or 'Image received'
# #             message_type = "Image"
# #         elif msg_type == 'audio':
# #             message_text = 'Audio message received'
# #             message_type = "Audio"
# #         elif msg_type == 'video':
# #             message_text = message_payload.get('caption', '') or 'Video received'
# #             message_type = "Video"
# #         elif msg_type == 'document':
# #             filename = message_payload.get('filename', 'document')
# #             message_text = f"Document received: {filename}"
# #             message_type = "Document"
# #         else:
# #             message_text = f"Unsupported message type: {msg_type}"
        
# #         # Fallback for empty message
# #         if not message_text:
# #             message_text = "Empty message received"
        
# #         # Gupshup message ID
# #         gupshup_message_id = payload.get('id', f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
# #         timestamp = payload.get('timestamp', '')
        
# #         # Clean phone numbers
# #         clean_source = clean_phone_number(source_phone)
# #         clean_destination = clean_phone_number(destination_phone)
        
# #         frappe.log_error(f"Processing INCOMING: {clean_source} -> {clean_destination}: {message_text[:50]}...", "WhatsApp Incoming")
        
# #         # Create incoming message document
# #         result = create_incoming_message_doc_enhanced(
# #             source_phone=clean_source,
# #             destination_phone=clean_destination,
# #             message=message_text,
# #             message_type=message_type,
# #             gupshup_message_id=gupshup_message_id,
# #             timestamp=timestamp
# #         )
        
# #         return result
        
# #     except Exception as e:
# #         frappe.log_error(f"Error processing incoming message: {str(e)}", "WhatsApp Incoming Error")
# #         return {"status": "error", "message": str(e)}

# # def create_incoming_message_doc_enhanced(source_phone, destination_phone, message, message_type="Text", 
# #                                        gupshup_message_id=None, timestamp=None):
# #     """Enhanced creation of WhatsApp Message document for incoming messages"""
# #     try:
# #         # Check for duplicate messages first
# #         if gupshup_message_id:
# #             existing = frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id})
# #             if existing:
# #                 frappe.log_error(f"Duplicate message ignored: {gupshup_message_id}", "WhatsApp Duplicate")
# #                 return {"status": "duplicate", "message": "Message already exists"}
        
# #         # Validate inputs
# #         if not source_phone or not message:
# #             return {"status": "error", "message": "Missing required fields"}
        
# #         # Generate message ID if not provided
# #         if not gupshup_message_id:
# #             gupshup_message_id = f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
# #         # Get or create contact for the sender
# #         contact_name = get_or_create_contact_safe(source_phone)
        
# #         # Parse timestamp
# #         parsed_timestamp = parse_timestamp(timestamp)
        
# #         # Create WhatsApp Message document with direction='Incoming'
# #         message_data = {
# #             "doctype": "WhatsApp Message",
# #             "source": source_phone,
# #             "destination": destination_phone or GUPSHUP_CONFIG["source_number"],
# #             "message": message[:1000],  # Limit message length
# #             "message_id": gupshup_message_id,
# #             "direction": "Incoming",  # This marks it as a received message
# #             "message_type": message_type,
# #             "status": "Delivered",
# #             "timestamp": parsed_timestamp,
# #         }
        
# #         # Add contact if available
# #         if contact_name:
# #             message_data["contact"] = contact_name
        
# #         # Create and insert the document
# #         message_doc = frappe.get_doc(message_data)
# #         message_doc.insert(ignore_permissions=True, ignore_mandatory=True)
# #         frappe.db.commit()
        
# #         # Update contact's last message info
# #         if contact_name:
# #             update_contact_last_message(contact_name, message, parsed_timestamp)
        
# #         frappe.log_error(f"✅ Created INCOMING message: {message_doc.name}", "WhatsApp Success")
        
# #         return {
# #             "status": "success", 
# #             "message_doc_name": message_doc.name,
# #             "direction": "Incoming",
# #             "source": source_phone,
# #             "destination": destination_phone,
# #             "message_id": gupshup_message_id,
# #             "message": message,
# #             "timestamp": parsed_timestamp.isoformat() if parsed_timestamp else None
# #         }
        
# #     except Exception as e:
# #         frappe.log_error(f"❌ Error creating incoming message: {str(e)}", "WhatsApp Document Error")
# #         return {"status": "error", "message": str(e)}

# # def get_or_create_contact_safe(phone_number):
# #     """Safely get or create Whatsapp Contact"""
# #     try:
# #         if not phone_number:
# #             return None
            
# #         clean_phone = clean_phone_number(phone_number)
        
# #         # Check if contact exists
# #         existing_contacts = frappe.get_all(
# #             "Whatsapp Contact",
# #             filters={"phone_number": clean_phone},
# #             fields=["name"],
# #             limit=1
# #         )
        
# #         if existing_contacts:
# #             return existing_contacts[0].name
        
# #         # Create new contact
# #         contact_name = get_contact_display_name(clean_phone)
        
# #         contact_data = {
# #             "doctype": "Whatsapp Contact",
# #             "phone_number": clean_phone,
# #             "name1": contact_name
# #         }
        
# #         # Add optional fields if they exist
# #         try:
# #             contact_data["opt_in_status"] = "Opted In"
# #         except:
# #             pass
        
# #         contact_doc = frappe.get_doc(contact_data)
# #         contact_doc.insert(ignore_permissions=True, ignore_mandatory=True)
# #         frappe.db.commit()
        
# #         frappe.log_error(f"Created contact: {contact_doc.name} for {clean_phone}", "Contact Created")
# #         return contact_doc.name
        
# #     except Exception as e:
# #         frappe.log_error(f"Contact creation failed for {phone_number}: {str(e)}", "Contact Error")
# #         return None

# # def update_contact_last_message(contact_name, message, timestamp):
# #     """Update contact's last message information"""
# #     try:
# #         frappe.db.set_value("Whatsapp Contact", contact_name, {
# #             "last_message_date": timestamp,
# #             "last_message": message[:100]
# #         })
# #         frappe.db.commit()
# #     except Exception as e:
# #         frappe.log_error(f"Failed to update contact last message: {str(e)}", "Contact Update Error")

# # def parse_timestamp(timestamp):
# #     """Parse timestamp from various formats"""
# #     try:
# #         if not timestamp:
# #             return datetime.now()
        
# #         if isinstance(timestamp, str):
# #             timestamp = int(timestamp)
        
# #         # Gupshup usually sends timestamp in milliseconds
# #         if timestamp > 1000000000000:  # If timestamp is in milliseconds
# #             return datetime.fromtimestamp(timestamp / 1000)
# #         else:  # If timestamp is in seconds
# #             return datetime.fromtimestamp(timestamp)
# #     except:
# #         return datetime.now()

# # def clean_phone_number(phone_number):
# #     """Clean and standardize phone number"""
# #     if not phone_number:
# #         return phone_number
        
# #     # Remove spaces, dashes, parentheses
# #     clean = str(phone_number).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
# #     # Remove + if present
# #     if clean.startswith('+'):
# #         clean = clean[1:]
    
# #     # Add 91 if it's a 10-digit Indian number
# #     if len(clean) == 10 and clean.isdigit():
# #         clean = '91' + clean
    
# #     return clean

# # def get_contact_display_name(phone_number):
# #     """Generate a display name for the contact"""
# #     clean_phone = clean_phone_number(phone_number)
    
# #     if clean_phone == GUPSHUP_CONFIG["source_number"]:
# #         return "Your Business"
# #     else:
# #         return f"Contact {clean_phone[-4:]}"

# # # Enhanced sending functions for the chat interface
# # @frappe.whitelist()
# # def send_whatsapp_message_enhanced(destination, message, message_id=None):
# #     """Enhanced WhatsApp message sending with better error handling"""
# #     try:
# #         # Clean destination number
# #         clean_destination = clean_phone_number(destination)
        
# #         if not clean_destination or not message:
# #             return {
# #                 "success": False,
# #                 "error": "Missing destination or message"
# #             }
        
# #         # Generate message ID if not provided
# #         if not message_id:
# #             message_id = f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
# #         # Prepare message data for Gupshup
# #         message_data = {
# #             'type': 'text',
# #             'text': str(message)[:1000]  # Limit message length
# #         }
        
# #         # Prepare form data for Gupshup API
# #         form_data = {
# #             'channel': 'whatsapp',
# #             'source': GUPSHUP_CONFIG["source_number"],
# #             'destination': clean_destination,
# #             'message': json.dumps(message_data),
# #             'src.name': GUPSHUP_CONFIG["app_name"]
# #         }
        
# #         # Make API call to Gupshup
# #         success, response_data, error_msg = make_gupshup_api_call_enhanced(form_data)
        
# #         # Create outgoing message record
# #         create_result = create_outgoing_message_doc(
# #             destination=clean_destination,
# #             message=message,
# #             message_id=message_id,
# #             status="Sent" if success else "Failed"
# #         )
        
# #         frappe.log_error(f"📤 Sent message to {clean_destination}: {'Success' if success else 'Failed'}", "WhatsApp Sent")
        
# #         return {
# #             "success": success,
# #             "message": "Message sent successfully" if success else f"Failed to send: {error_msg}",
# #             "message_id": message_id,
# #             "destination": clean_destination,
# #             "direction": "Outgoing",
# #             "frappe_doc": create_result.get("doc_name") if create_result.get("status") == "success" else None,
# #             "timestamp": datetime.now().isoformat()
# #         }
        
# #     except Exception as e:
# #         frappe.log_error(f"Send message error: {str(e)}", "Send Message Error")
# #         return {
# #             "success": False,
# #             "error": str(e)
# #         }

# # def create_outgoing_message_doc(destination, message, message_id, status="Sent"):
# #     """Create WhatsApp Message document for outgoing messages"""
# #     try:
# #         # Get or create contact
# #         contact_name = get_or_create_contact_safe(destination)
        
# #         message_data = {
# #             "doctype": "WhatsApp Message",
# #             "source": GUPSHUP_CONFIG["source_number"],
# #             "destination": destination,
# #             "message": message[:1000],
# #             "message_id": message_id,
# #             "direction": "Outgoing",
# #             "message_type": "Text",
# #             "status": status,
# #             "timestamp": datetime.now(),
# #         }
        
# #         if contact_name:
# #             message_data["contact"] = contact_name
        
# #         message_doc = frappe.get_doc(message_data)
# #         message_doc.insert(ignore_permissions=True, ignore_mandatory=True)
# #         frappe.db.commit()
        
# #         return {"status": "success", "doc_name": message_doc.name}
        
# #     except Exception as e:
# #         frappe.log_error(f"Failed to create outgoing message doc: {str(e)}", "Outgoing Doc Error")
# #         return {"status": "error", "message": str(e)}

# # def make_gupshup_api_call_enhanced(form_data):
# #     """Enhanced API call to Gupshup with better error handling"""
# #     try:
# #         # Encode the data
# #         data = urllib.parse.urlencode(form_data).encode('utf-8')
        
# #         # Create the request
# #         req = urllib.request.Request(
# #             GUPSHUP_CONFIG["api_endpoint"],
# #             data=data,
# #             headers={
# #                 'apikey': GUPSHUP_CONFIG["api_key"],
# #                 'Content-Type': 'application/x-www-form-urlencoded'
# #             }
# #         )
        
# #         # Make the API call
# #         with urllib.request.urlopen(req, timeout=30) as response:
# #             response_data = response.read().decode('utf-8')
            
# #         return True, response_data, None
        
# #     except Exception as api_error:
# #         error_msg = str(api_error)
# #         frappe.log_error(f"Gupshup API Error: {error_msg}", "Gupshup API Error")
# #         return False, None, error_msg

# # def process_delivery_report(data):
# #     """Process delivery report from Gupshup"""
# #     try:
# #         payload = data.get('payload', {})
# #         message_id = payload.get('gsId', '')
# #         event_type = payload.get('type', '').lower()
        
# #         # Map Gupshup event types to our status
# #         status_mapping = {
# #             "sent": "Sent",
# #             "delivered": "Delivered", 
# #             "read": "Read",
# #             "failed": "Failed",
# #             "enroute": "Sent"
# #         }
        
# #         new_status = status_mapping.get(event_type, "Sent")
        
# #         # Find and update the message
# #         message_docs = frappe.get_all(
# #             "WhatsApp Message",
# #             filters={"message_id": message_id},
# #             fields=["name", "status"],
# #             limit=1
# #         )
        
# #         if message_docs:
# #             message_doc = message_docs[0]
# #             if message_doc.status != new_status:
# #                 frappe.db.set_value("WhatsApp Message", message_doc.name, "status", new_status)
# #                 frappe.db.commit()
            
# #             return {"status": "success", "message": f"Status updated to {new_status}"}
# #         else:
# #             return {"status": "not_found", "message": "Message not found"}
            
# #     except Exception as e:
# #         frappe.log_error(f"Error processing delivery report: {str(e)}", "WhatsApp Delivery Error")
# #         return {"status": "error", "message": str(e)}

# # def process_user_event(data):
# #     """Process user events like opt-in/opt-out"""
# #     try:
# #         payload = data.get('payload', {})
# #         phone_number = payload.get('phone', '')
# #         event_type = payload.get('type', '')
        
# #         if phone_number and event_type in ['opt-in', 'opt-out']:
# #             clean_phone = clean_phone_number(phone_number)
# #             status = "Opted In" if event_type == 'opt-in' else "Opted Out"
            
# #             contact = get_or_create_contact_safe(clean_phone)
# #             if contact:
# #                 try:
# #                     frappe.db.set_value("Whatsapp Contact", contact, "opt_in_status", status)
# #                     frappe.db.commit()
# #                 except:
# #                     pass
        
# #         return {"status": "success", "message": "User event processed"}
        
# #     except Exception as e:
# #         frappe.log_error(f"Error processing user event: {str(e)}", "WhatsApp User Event Error")
# #         return {"status": "error", "message": str(e)}

# # @frappe.whitelist()
# # def get_recent_messages_enhanced(contact_phone, limit=50):
# #     """Enhanced function to get recent messages for real-time updates"""
# #     try:
# #         if not contact_phone:
# #             return {"status": "error", "message": "Contact phone number is required"}
        
# #         contact_phone = str(contact_phone).strip()
# #         clean_phone = contact_phone.replace('+', '') if contact_phone.startswith('+') else contact_phone
        
# #         if not GUPSHUP_CONFIG or not GUPSHUP_CONFIG.get("source_number"):
# #             return {"status": "error", "message": "WhatsApp configuration not found"}
            
# #         our_number = str(GUPSHUP_CONFIG["source_number"]).strip()
        
# #         try:
# #             limit = int(limit)
# #             if limit <= 0 or limit > 1000:
# #                 limit = 50
# #         except:
# #             limit = 50
       
# #         # Get all messages for this contact (both incoming and outgoing)
# #         messages = frappe.db.sql("""
# #             SELECT name, source, destination, message, direction, message_type, 
# #                    status, timestamp, message_id, creation, modified
# #             FROM `tabWhatsApp Message`
# #             WHERE (source = %s AND destination = %s) 
# #                OR (source = %s AND destination = %s)
# #             ORDER BY creation DESC
# #             LIMIT %s
# #         """, (clean_phone, our_number, our_number, clean_phone, limit), as_dict=True)
        
# #         # Format timestamps for better frontend handling
# #         for message in messages:
# #             if message.get('timestamp'):
# #                 message['formatted_timestamp'] = frappe.utils.get_datetime(message['timestamp']).isoformat()
# #             if message.get('creation'):
# #                 message['formatted_creation'] = frappe.utils.get_datetime(message['creation']).isoformat()
       
# #         return {
# #             "status": "success",
# #             "messages": messages,
# #             "contact_phone": clean_phone,
# #             "total_count": len(messages)
# #         }
       
# #     except Exception as e:
# #         frappe.log_error(f"Error getting recent messages for {contact_phone}: {str(e)}", "WhatsApp Messages Error")
# #         return {"status": "error", "message": "An error occurred while fetching messages"}

# # # Test and debugging functions
# # @frappe.whitelist()
# # def test_incoming_message():
# #     """Test function to simulate incoming message"""
# #     try:
# #         test_data = {
# #             "type": "message",
# #             "payload": {
# #                 "id": f"test_incoming_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
# #                 "source": "919876543210",
# #                 "destination": GUPSHUP_CONFIG["source_number"],
# #                 "timestamp": str(int(datetime.now().timestamp() * 1000)),
# #                 "payload": {
# #                     "type": "text",
# #                     "text": "This is a test incoming message"
# #                 }
# #             }
# #         }
        
# #         result = process_incoming_message_enhanced(test_data)
        
# #         return {
# #             "status": "success",
# #             "message": "Test incoming message processed",
# #             "result": result
# #         }
        
# #     except Exception as e:
# #         return {"status": "error", "message": str(e)}

# # @frappe.whitelist(allow_guest=True)
# # def simple_test():
# #     """Simple test endpoint"""
# #     return {
# #         "status": "success", 
# #         "message": "Webhook endpoint is working!", 
# #         "timestamp": str(datetime.now()),
# #         "method": frappe.request.method
# #     }

# # # Legacy function aliases for backward compatibility
# # send_whatsapp_message = send_whatsapp_message_enhanced
# # get_recent_messages = get_recent_messages_enhanced


# import frappe
# from frappe import _
# import json
# import urllib.parse
# import urllib.request
# from datetime import datetime

# # Gupshup Configuration
# GUPSHUP_CONFIG = {
#     "api_key": "qpk4f7vilyb0ef8oeawrflbsap055zmt",
#     "source_number": "919746574552",
#     "api_endpoint": "https://api.gupshup.io/sm/api/v1/msg",
#     "app_name": "smartschool"
# }

# @frappe.whitelist(allow_guest=True)
# def handle_gupshup_webhook():
#     """
#     Main webhook endpoint to receive incoming WhatsApp messages from Gupshup
#     URL: https://smartschool.prismaticsoft.com/api/method/whatsapp_manager.api.webhook.handle_gupshup_webhook
#     """
#     try:
#         # Log the request method
#         frappe.log_error(f"Webhook called with method: {frappe.request.method}", "WhatsApp Webhook Debug")
        
#         # Get the request data - try multiple methods
#         data = None
        
#         # Method 1: Try JSON data first
#         if hasattr(frappe.request, 'get_json'):
#             try:
#                 data = frappe.request.get_json(force=True)
#             except:
#                 pass
        
#         # Method 2: Try form data
#         if not data:
#             data = frappe.local.form_dict
        
#         # Method 3: Try raw data
#         if not data and hasattr(frappe.request, 'get_data'):
#             try:
#                 raw_data = frappe.request.get_data(as_text=True)
#                 if raw_data:
#                     data = json.loads(raw_data)
#             except:
#                 pass
        
#         # Log the received data for debugging
#         frappe.log_error(f"Webhook received data: {json.dumps(data, indent=2) if data else 'No data'}", "WhatsApp Webhook Data")
        
#         if not data:
#             return {"status": "error", "message": "No data received"}
        
#         # Check if this is a verification request (some platforms send these)
#         if 'hub.challenge' in data:
#             return data.get('hub.challenge')
        
#         # Extract message information from webhook
#         message_type = data.get('type', 'message')
        
#         if message_type == 'message':
#             return process_incoming_message(data)
#         elif message_type == 'message-event':
#             return process_delivery_report(data)
#         elif message_type == 'user-event':
#             return process_user_event(data)
#         else:
#             frappe.log_error(f"Unknown webhook type: {message_type}", "WhatsApp Webhook")
#             return {"status": "success", "message": f"Ignored type: {message_type}"}
            
#     except Exception as e:
#         error_msg = str(e)
#         frappe.log_error(f"Webhook error: {error_msg}\nData: {frappe.local.form_dict}", "WhatsApp Webhook Error")
#         return {"status": "error", "message": error_msg}

# def process_incoming_message(data):
#     """Process incoming WhatsApp message and create it with direction='Incoming'"""
#     try:
#         # Extract message details from webhook format
#         payload = data.get('payload', {})
        
#         # Source phone number (sender) - this is who sent the message TO us
#         source_phone = payload.get('source', '')
        
#         # Destination should be our business number
#         destination_phone = payload.get('destination', GUPSHUP_CONFIG["source_number"])
        
#         # Message content
#         message_payload = payload.get('payload', {})
#         message_text = ""
#         message_type = "Text"
#         media_url = None
#         media_type = None
        
#         # Handle different message types from Gupshup
#         msg_type = message_payload.get('type', 'text')
        
#         if msg_type == 'text':
#             message_text = message_payload.get('text', '')
#         elif msg_type == 'image':
#             message_text = message_payload.get('caption', '') or 'Image received'
#             message_type = "Image"
#             media_url = message_payload.get('url', '')
#             media_type = "image"
#         elif msg_type == 'audio':
#             message_text = message_payload.get('caption', '') or 'Audio message received'
#             message_type = "Audio"
#             media_url = message_payload.get('url', '')
#             media_type = "audio"
#         elif msg_type == 'video':
#             message_text = message_payload.get('caption', '') or 'Video received'
#             message_type = "Video"
#             media_url = message_payload.get('url', '')
#             media_type = "video"
#         elif msg_type == 'file' or msg_type == 'document':
#             filename = message_payload.get('filename', 'document')
#             message_text = f"Document received: {filename}"
#             message_type = "Document"
#             media_url = message_payload.get('url', '')
#             media_type = "document"
#         elif msg_type == 'location':
#             lat = message_payload.get('latitude', 0)
#             lng = message_payload.get('longitude', 0)
#             message_text = f"Location shared: {lat}, {lng}"
#             message_type = "Location"
#         elif msg_type == 'contact':
#             contact_name = message_payload.get('name', 'Contact')
#             message_text = f"Contact shared: {contact_name}"
#             message_type = "Contact"
#         else:
#             message_text = f"Unsupported message type: {msg_type}"
        
#         # Gupshup message ID
#         gupshup_message_id = payload.get('id', '')
#         timestamp = payload.get('timestamp', '')
        
#         # Clean phone numbers
#         clean_source = clean_phone_number(source_phone)
#         clean_destination = clean_phone_number(destination_phone)
        
#         frappe.log_error(f"Processing INCOMING message from {clean_source} to {clean_destination}: {message_text}", "WhatsApp Incoming")
        
#         # Create incoming message document with direction='Incoming'
#         result = create_incoming_message_doc(
#             source_phone=clean_source,
#             destination_phone=clean_destination,
#             message=message_text,
#             message_type=message_type,
#             media_url=media_url,
#             media_type=media_type,
#             gupshup_message_id=gupshup_message_id,
#             timestamp=timestamp
#         )
        
#         return result
        
#     except Exception as e:
#         frappe.log_error(f"Error processing incoming message: {str(e)}", "WhatsApp Incoming Error")
#         return {"status": "error", "message": str(e)}

# def create_incoming_message_doc(source_phone, destination_phone, message, message_type="Text", 
#                                media_url=None, media_type=None, gupshup_message_id=None, timestamp=None):
#     """Create WhatsApp Message document for incoming message with direction='Incoming'"""
#     try:
#         # Check for duplicate messages first
#         if gupshup_message_id:
#             existing = frappe.db.exists("WhatsApp Message", {"message_id": gupshup_message_id})
#             if existing:
#                 frappe.log_error(f"Duplicate message ignored: {gupshup_message_id}", "WhatsApp Duplicate")
#                 return {"status": "duplicate", "message": "Message already exists"}
        
#         # Generate message ID if not provided
#         if not gupshup_message_id:
#             gupshup_message_id = f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
#         # Get or create contacts
#         source_contact = get_or_create_contact(source_phone)
#         destination_contact = get_or_create_contact(destination_phone)
        
#         # Parse timestamp
#         parsed_timestamp = None
#         if timestamp:
#             try:
#                 # Gupshup usually sends timestamp in milliseconds
#                 if isinstance(timestamp, str):
#                     timestamp = int(timestamp)
#                 parsed_timestamp = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1000000000000 else timestamp)
#             except:
#                 parsed_timestamp = datetime.now()
#         else:
#             parsed_timestamp = datetime.now()
        
#         # Create WhatsApp Message document with direction='Incoming'
#         message_data = {
#             "doctype": "WhatsApp Message",
#             "source": source_phone,  # Phone number of sender (customer)
#             "destination": destination_phone,  # Our business number
#             "message": message,
#             "message_id": gupshup_message_id,
#             "direction": "Incoming",  # This is crucial - marks it as received message
#             "message_type": message_type,
#             "status": "Delivered",  # Incoming messages are automatically delivered
#             "timestamp": parsed_timestamp,
#             "creation": parsed_timestamp,
#             "modified": parsed_timestamp
#         }
        
#         # Add optional fields if they exist in the doctype
#         if media_url:
#             message_data["media_url"] = media_url
#         if media_type:
#             message_data["media_type"] = media_type
#         if source_contact:
#             message_data["contact"] = source_contact
            
#         # Try to add other fields that might exist
#         try:
#             message_data["content"] = f"Received: {message}"[:140]
#         except:
#             pass
            
#         try:
#             message_data["sender_name"] = get_contact_name(source_phone)
#         except:
#             pass
        
#         # Create and insert the document
#         message_doc = frappe.get_doc(message_data)
#         message_doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         # Update last message date on sender contact
#         if source_contact:
#             try:
#                 frappe.db.set_value("Whatsapp Contact", source_contact, {
#                     "last_message_date": parsed_timestamp,
#                     "last_message": message[:100]
#                 })
#                 frappe.db.commit()
#             except Exception as contact_update_error:
#                 frappe.log_error(f"Error updating contact: {str(contact_update_error)}", "Contact Update Error")
        
#         frappe.log_error(f"✅ Successfully created INCOMING message: {message_doc.name} from {source_phone}", "WhatsApp Success")
        
#         return {
#             "status": "success", 
#             "message_doc_name": message_doc.name,
#             "direction": "Incoming",
#             "source": source_phone,
#             "destination": destination_phone,
#             "message_id": gupshup_message_id,
#             "message": message,
#             "timestamp": parsed_timestamp.isoformat() if parsed_timestamp else None
#         }
        
#     except Exception as e:
#         frappe.log_error(f"❌ Error creating incoming message doc: {str(e)}\nData: {locals()}", "WhatsApp Document Error")
#         return {"status": "error", "message": str(e)}

# def get_or_create_contact(phone_number):
#     """Get or create Whatsapp Contact with better error handling"""
#     try:
#         clean_phone = clean_phone_number(phone_number)
        
#         # Try to find existing contact
#         existing_contact = frappe.get_all(
#             "Whatsapp Contact",
#             filters={"phone_number": clean_phone},
#             fields=["name"],
#             limit=1
#         )
        
#         if existing_contact:
#             return existing_contact[0].name
        
#         # Create new contact
#         try:
#             contact_name = get_contact_name(clean_phone)
            
#             contact_doc = frappe.get_doc({
#                 "doctype": "Whatsapp Contact",
#                 "phone_number": clean_phone,
#                 "name1": contact_name
#             })
            
#             # Add opt_in_status if field exists
#             try:
#                 contact_doc.opt_in_status = "Opted In"
#             except:
#                 pass
            
#             # Add other optional fields
#             try:
#                 if clean_phone == GUPSHUP_CONFIG["source_number"]:
#                     contact_doc.is_business = 1
#             except:
#                 pass
                
#             contact_doc.insert(ignore_permissions=True)
#             frappe.db.commit()
            
#             frappe.log_error(f"Created new contact: {contact_doc.name} for {clean_phone}", "Contact Created")
#             return contact_doc.name
            
#         except Exception as contact_error:
#             frappe.log_error(f"Contact creation failed for {clean_phone}: {str(contact_error)}", "Contact Creation Error")
#             return None
            
#     except Exception as e:
#         frappe.log_error(f"Error in get_or_create_contact for {phone_number}: {str(e)}", "Contact Error")
#         return None

# def clean_phone_number(phone_number):
#     """Clean and standardize phone number"""
#     if not phone_number:
#         return phone_number
        
#     # Remove spaces, dashes, parentheses
#     clean = str(phone_number).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
#     # Remove + if present
#     if clean.startswith('+'):
#         clean = clean[1:]
    
#     # Add 91 if it's a 10-digit Indian number
#     if len(clean) == 10 and clean.isdigit():
#         clean = '91' + clean
    
#     return clean

# def get_contact_name(phone_number):
#     """Generate a contact name from phone number"""
#     clean_phone = clean_phone_number(phone_number)
    
#     if clean_phone == GUPSHUP_CONFIG["source_number"]:
#         return "Your Business"
#     else:
#         return f"Contact {clean_phone[-4:]}"

# def process_delivery_report(data):
#     """Process delivery report from Gupshup"""
#     try:
#         payload = data.get('payload', {})
#         message_id = payload.get('gsId', '')
#         event_type = payload.get('type', '').lower()
#         timestamp = payload.get('timestamp', '')
        
#         # Map Gupshup event types to our status
#         status_mapping = {
#             "sent": "Sent",
#             "delivered": "Delivered", 
#             "read": "Read",
#             "failed": "Failed",
#             "enroute": "Sent"
#         }
        
#         new_status = status_mapping.get(event_type, "Sent")
        
#         # Find and update the message
#         message_docs = frappe.get_all(
#             "WhatsApp Message",
#             filters={"message_id": message_id},
#             fields=["name", "status"],
#             limit=1
#         )
        
#         if message_docs:
#             message_doc = message_docs[0]
#             old_status = message_doc.status
            
#             # Only update if status is actually changing
#             if old_status != new_status:
#                 frappe.db.set_value("WhatsApp Message", message_doc.name, "status", new_status)
#                 frappe.db.commit()
                
#                 frappe.log_error(f"📋 Updated message {message_id} status: {old_status} → {new_status}", "WhatsApp Status Update")
            
#             return {"status": "success", "message": f"Status updated to {new_status}"}
#         else:
#             frappe.log_error(f"❌ Delivery report for unknown message: {message_id}", "WhatsApp Unknown Message")
#             return {"status": "not_found", "message": "Message not found"}
            
#     except Exception as e:
#         frappe.log_error(f"Error processing delivery report: {str(e)}", "WhatsApp Delivery Error")
#         return {"status": "error", "message": str(e)}

# def process_user_event(data):
#     """Process user events like opt-in/opt-out"""
#     try:
#         payload = data.get('payload', {})
#         phone_number = payload.get('phone', '')
#         event_type = payload.get('type', '')
        
#         if phone_number and event_type in ['opt-in', 'opt-out']:
#             clean_phone = clean_phone_number(phone_number)
#             status = "Opted In" if event_type == 'opt-in' else "Opted Out"
            
#             # Update or create contact
#             contact = get_or_create_contact(clean_phone)
#             if contact:
#                 try:
#                     frappe.db.set_value("Whatsapp Contact", contact, "opt_in_status", status)
#                     frappe.db.commit()
#                 except:
#                     pass
            
#             frappe.log_error(f"User event: {phone_number} {event_type}", "WhatsApp User Event")
        
#         return {"status": "success", "message": "User event processed"}
        
#     except Exception as e:
#         frappe.log_error(f"Error processing user event: {str(e)}", "WhatsApp User Event Error")
#         return {"status": "error", "message": str(e)}

# # Enhanced sending functions for the chat interface

# @frappe.whitelist()
# def send_whatsapp_message(destination, message, message_id=None):
#     """Send WhatsApp message via Gupshup API and create outgoing record"""
#     try:
#         # Clean destination number
#         clean_destination = clean_phone_number(destination)
        
#         # Generate message ID if not provided
#         if not message_id:
#             message_id = f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
#         # Prepare message data for Gupshup
#         message_data = {
#             'type': 'text',
#             'text': str(message)
#         }
        
#         # Prepare form data for Gupshup API
#         form_data = {
#             'channel': 'whatsapp',
#             'source': GUPSHUP_CONFIG["source_number"],
#             'destination': clean_destination,
#             'message': json.dumps(message_data),
#             'src.name': GUPSHUP_CONFIG["app_name"]
#         }
        
#         # Make API call to Gupshup
#         success, response_data, error_msg = make_gupshup_api_call(form_data)
        
#         # Create WhatsApp Message record with direction='Outgoing'
#         message_doc_data = {
#             "doctype": "WhatsApp Message",
#             "source": GUPSHUP_CONFIG["source_number"],  # Our business number
#             "destination": clean_destination,  # Customer's number
#             "message": message,
#             "message_id": message_id,
#             "direction": "Outgoing",  # This marks it as sent message
#             "message_type": "Text",
#             "status": "Sent" if success else "Failed",
#             "timestamp": datetime.now()
#         }
        
#         # Add contact if exists
#         destination_contact = get_or_create_contact(clean_destination)
#         if destination_contact:
#             message_doc_data["contact"] = destination_contact
        
#         message_doc = frappe.get_doc(message_doc_data)
#         message_doc.insert(ignore_permissions=True)
#         frappe.db.commit()
        
#         frappe.log_error(f"📤 Created OUTGOING message: {message_doc.name} to {clean_destination}", "WhatsApp Sent")
        
#         return {
#             "success": success,
#             "message": "Message sent successfully" if success else f"Failed to send: {error_msg}",
#             "gupshup_response": response_data,
#             "frappe_doc": message_doc.name,
#             "message_id": message_id,
#             "destination": clean_destination,
#             "direction": "Outgoing",
#             "timestamp": datetime.now().isoformat()
#         }
        
#     except Exception as e:
#         frappe.log_error(f"Send message error: {str(e)}", "Send Message Error")
#         return {
#             "success": False,
#             "error": str(e)
#         }

# def make_gupshup_api_call(form_data):
#     """Make API call to Gupshup"""
#     try:
#         # Encode the data
#         data = urllib.parse.urlencode(form_data).encode('utf-8')
        
#         # Create the request
#         req = urllib.request.Request(
#             GUPSHUP_CONFIG["api_endpoint"],
#             data=data,
#             headers={
#                 'apikey': GUPSHUP_CONFIG["api_key"],
#                 'Content-Type': 'application/x-www-form-urlencoded'
#             }
#         )
        
#         # Make the API call
#         with urllib.request.urlopen(req, timeout=30) as response:
#             response_data = response.read().decode('utf-8')
            
#         frappe.log_error(f"Gupshup API Response: {response_data}", "Gupshup API Success")
#         return True, response_data, None
        
#     except Exception as api_error:
#         error_msg = str(api_error)
#         frappe.log_error(f"Gupshup API Error: {error_msg}", "Gupshup API Error")
#         return False, f"API Error: {error_msg}", error_msg

# @frappe.whitelist()
# def test_webhook():
#     """Test webhook functionality by simulating incoming message"""
#     try:
#         # Simulate incoming message data from Gupshup
#         test_data = {
#             "type": "message",
#             "payload": {
#                 "id": f"test_incoming_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
#                 "source": "919876543210",  # Test customer number
#                 "destination": GUPSHUP_CONFIG["source_number"],  # Our business number
#                 "timestamp": str(int(datetime.now().timestamp() * 1000)),
#                 "payload": {
#                     "type": "text",
#                     "text": "This is a test incoming message to verify webhook functionality"
#                 }
#             }
#         }
        
#         result = process_incoming_message(test_data)
        
#         return {
#             "status": "success",
#             "message": "Webhook test completed - incoming message created",
#             "result": result,
#             "test_data": test_data
#         }
        
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# @frappe.whitelist()
# def get_webhook_logs(limit=20):
#     """Get recent webhook logs for debugging"""
#     try:
#         logs = frappe.get_all(
#             "Error Log",
#             filters=[
#                 ["error", "like", "%WhatsApp%"]
#             ],
#             fields=["name", "error", "creation", "method"],
#             order_by="creation desc",
#             limit=limit
#         )
        
#         return {
#             "status": "success",
#             "logs": logs
#         }
        
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# # Legacy webhook functions for compatibility
# @frappe.whitelist(allow_guest=True)
# def gupshup_webhook():
#     """Legacy webhook function - redirects to main handler"""
#     return handle_gupshup_webhook()

# @frappe.whitelist(allow_guest=True)
# def simple_test():
#     """Ultra-simple test endpoint"""
#     return {
#         "status": "success", 
#         "message": "Webhook endpoint is working!", 
#         "timestamp": str(datetime.now()),
#         "method": frappe.request.method,
#         "headers": dict(frappe.request.headers) if hasattr(frappe.request, 'headers') else {},
#         "form_data": frappe.local.form_dict
#     }


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

@frappe.whitelist()
def get_recent_messages(contact_phone, limit=50):
    """Get recent messages for a contact (for real-time updates)"""
    try:
        # Input validation
        if not contact_phone:
            return {
                "status": "error",
                "message": "Contact phone number is required"
            }
        
        # Ensure contact_phone is a string
        contact_phone = str(contact_phone).strip()
        
        # Clean phone number - remove + prefix if present
        clean_phone = contact_phone.replace('+', '') if contact_phone.startswith('+') else contact_phone
        
        # Validate that we have GUPSHUP_CONFIG
        if not GUPSHUP_CONFIG or not GUPSHUP_CONFIG.get("source_number"):
            return {
                "status": "error",
                "message": "WhatsApp configuration not found"
            }
            
        our_number = str(GUPSHUP_CONFIG["source_number"]).strip()
        
        # Validate limit parameter
        try:
            limit = int(limit)
            if limit <= 0 or limit > 1000:  # Set reasonable bounds
                limit = 50
        except (ValueError, TypeError):
            limit = 50
       
        # Get messages where source or destination matches the contact
        # Method 1: Get incoming messages (from contact to us)
        incoming_messages = frappe.get_all(
            "WhatsApp Message",
            filters={
                "source": clean_phone,
                "destination": our_number
            },
            fields=[
                "name", "source", "destination", "message", "direction", 
                "message_type", "status", "timestamp", "message_id", 
                "creation", "modified"
            ],
            order_by="creation desc",
            limit=limit
        )
        
        # Method 2: Get outgoing messages (from us to contact)
        outgoing_messages = frappe.get_all(
            "WhatsApp Message",
            filters={
                "source": our_number,
                "destination": clean_phone
            },
            fields=[
                "name", "source", "destination", "message", "direction", 
                "message_type", "status", "timestamp", "message_id", 
                "creation", "modified"
            ],
            order_by="creation desc",
            limit=limit
        )
        
        # Combine and sort messages
        messages = incoming_messages + outgoing_messages
        messages.sort(key=lambda x: x.get('creation'), reverse=True)
        messages = messages[:limit]  # Apply limit after sorting
        
        # Alternative Method using raw SQL (if the above doesn't work well):
        # messages = frappe.db.sql("""
        #     SELECT name, source, destination, message, direction, message_type, 
        #            status, timestamp, message_id, creation, modified
        #     FROM `tabWhatsApp Message`
        #     WHERE (source = %s AND destination = %s) 
        #        OR (source = %s AND destination = %s)
        #     ORDER BY creation DESC
        #     LIMIT %s
        # """, (clean_phone, our_number, our_number, clean_phone, limit), as_dict=True)
        
        # Format timestamps for better frontend handling
        for message in messages:
            if message.get('timestamp'):
                # Convert timestamp to ISO format if needed
                message['formatted_timestamp'] = frappe.utils.get_datetime(message['timestamp']).isoformat()
            if message.get('creation'):
                message['formatted_creation'] = frappe.utils.get_datetime(message['creation']).isoformat()
       
        return {
            "status": "success",
            "messages": messages,
            "contact_phone": clean_phone,
            "total_count": len(messages)
        }
       
    except frappe.DoesNotExistError:
        return {
            "status": "error",
            "message": "WhatsApp Message doctype not found"
        }
    except frappe.PermissionError:
        return {
            "status": "error", 
            "message": "Insufficient permissions to access messages"
        }
    except Exception as e:
        frappe.log_error(
            message=f"Error getting recent messages for {contact_phone}: {str(e)}", 
            title="WhatsApp Messages Error"
        )
        return {
            "status": "error",
            "message": "An error occurred while fetching messages"
        }


@frappe.whitelist()
def get_contact_info(contact_phone):
    """Get contact information along with recent messages"""
    try:
        if not contact_phone:
            return {"status": "error", "message": "Contact phone required"}
            
        contact_phone = str(contact_phone).strip()
        clean_phone = contact_phone.replace('+', '') if contact_phone.startswith('+') else contact_phone
        
        # Try to find contact in the system
        contact_info = None
        try:
            # Look for contact by phone number
            contacts = frappe.get_all(
                "Contact",
                filters={
                    "phone": ["like", f"%{clean_phone}%"]
                },
                fields=["name", "first_name", "last_name", "phone", "mobile_no"],
                limit=1
            )
            if contacts:
                contact_info = contacts[0]
        except:
            pass  # Contact not found, continue without it
        
        # Get recent messages
        messages_result = get_recent_messages(contact_phone, limit=20)
        
        return {
            "status": "success",
            "contact_info": contact_info,
            "messages": messages_result.get("messages", []),
            "phone": clean_phone
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting contact info: {str(e)}", "Contact Info Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist(allow_guest=True)
def debug_webhook():
    """Debug endpoint to test routing"""
    return {
        "status": "success",
        "message": "Webhook file is being called correctly",
        "timestamp": str(datetime.now())
    }        
@frappe.whitelist(allow_guest=True)
def handle_gupshup_webhook_fixed():
    """Fixed version of the main webhook without problematic logging"""
    try:
        # Get the request data without logging it (to avoid the 140 char limit)
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
        
        if not data:
            return {"status": "error", "message": "No data received"}
        
        # Check if this is a verification request
        if 'hub.challenge' in data:
            return data.get('hub.challenge')
        
        # Extract message information from webhook
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            return process_incoming_message_simple(data)
        elif message_type == 'message-event':
            return {"status": "success", "message": "Delivery report received"}
        elif message_type == 'user-event':
            return {"status": "success", "message": "User event received"}
        else:
            return {"status": "success", "message": f"Ignored type: {message_type}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_incoming_message_simple(data):
    """Simplified message processing without extensive logging"""
    try:
        # Extract message details
        payload = data.get('payload', {})
        source_phone = payload.get('source', '')
        destination_phone = payload.get('destination', GUPSHUP_CONFIG["source_number"])
        
        # Message content
        message_payload = payload.get('payload', {})
        message_text = message_payload.get('text', 'No text content')
        
        # Clean phone numbers
        clean_source = clean_phone_number(source_phone)
        clean_destination = clean_phone_number(destination_phone)
        
        # For now, just return success without creating the document
        # This will help us test if the webhook processing works
        return {
            "status": "success",
            "message": "Message processed successfully",
            "source": clean_source,
            "destination": clean_destination,
            "text": message_text,
            "type": data.get('type')
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
    

@frappe.whitelist(allow_guest=True)
def handle_gupshup_webhook_complete():
    """Complete webhook that saves to database and sends replies"""
    try:
        # Get the request data
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
        
        if not data:
            return {"status": "error", "message": "No data received"}
        
        # Check if this is a verification request
        if 'hub.challenge' in data:
            return data.get('hub.challenge')
        
        # Extract message information from webhook
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            return process_and_reply_message(data)
        elif message_type == 'message-event':
            return {"status": "success", "message": "Delivery report received"}
        elif message_type == 'user-event':
            return {"status": "success", "message": "User event received"}
        else:
            return {"status": "success", "message": f"Ignored type: {message_type}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_and_reply_message(data):
    """Process incoming message, save to database, and send reply"""
    try:
        # Extract message details
        payload = data.get('payload', {})
        source_phone = payload.get('source', '')
        destination_phone = payload.get('destination', GUPSHUP_CONFIG["source_number"])
        
        # Message content
        message_payload = payload.get('payload', {})
        message_text = message_payload.get('text', 'No text content')
        message_id = payload.get('id', f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
        
        # Clean phone numbers
        clean_source = clean_phone_number(source_phone)
        clean_destination = clean_phone_number(destination_phone)
        
        # 1. Save incoming message to database
        saved_message = save_incoming_message_to_db(
            source=clean_source,
            destination=clean_destination,
            message=message_text,
            message_id=message_id
        )
        
        # 2. Generate and send reply
        reply_text = generate_reply(message_text, clean_source)
        reply_result = send_reply_message(clean_source, reply_text)
        
        return {
            "status": "success",
            "message": "Message received, saved, and reply sent",
            "incoming_message": {
                "doc_name": saved_message.get("doc_name"),
                "source": clean_source,
                "text": message_text
            },
            "reply_sent": {
                "success": reply_result.get("success"),
                "text": reply_text
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_incoming_message_to_db(source, destination, message, message_id):
    """Save incoming message to WhatsApp Message doctype"""
    try:
        # Check for duplicate messages
        existing = frappe.db.exists("WhatsApp Message", {"message_id": message_id})
        if existing:
            return {"status": "duplicate", "doc_name": existing}
        
        # Get or create contact
        contact = get_or_create_contact(source)
        
        # Create WhatsApp Message document
        message_doc = frappe.get_doc({
            "doctype": "WhatsApp Message",
            "source": source,
            "destination": destination,
            "message": message,
            "message_id": message_id,
            "direction": "Incoming",
            "message_type": "Text",
            "status": "Delivered",
            "timestamp": datetime.now(),
            "contact": contact
        })
        
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "status": "success",
            "doc_name": message_doc.name
        }
        
    except Exception as e:
        # If database save fails, log it but don't break the webhook
        frappe.log_error(f"DB save failed: {str(e)}", "DB Save Error")
        return {"status": "error", "message": str(e)}

def generate_reply(incoming_message, sender_phone):
    """Generate automatic reply based on incoming message"""
    incoming_lower = incoming_message.lower().strip()
    
    # Simple auto-reply logic
    if "hello" in incoming_lower or "hi" in incoming_lower:
        return "Hello! Thank you for contacting us. How can we help you today?"
    elif "help" in incoming_lower:
        return "We're here to help! Please describe your query and our team will assist you."
    elif "demo" in incoming_lower:
        return "Thanks for trying our demo! This is an automated response to show the webhook is working."
    elif "price" in incoming_lower or "cost" in incoming_lower:
        return "For pricing information, please contact our sales team or visit our website."
    else:
        return f"Thank you for your message: '{incoming_message}'. We have received it and will respond soon!"

def send_reply_message(destination_phone, reply_text):
    """Send reply message via Gupshup API"""
    try:
        # Generate message ID for the reply
        reply_message_id = f"reply_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Prepare message data for Gupshup
        message_data = {
            'type': 'text',
            'text': str(reply_text)
        }
        
        # Prepare form data for Gupshup API
        form_data = {
            'channel': 'whatsapp',
            'source': GUPSHUP_CONFIG["source_number"],
            'destination': destination_phone,
            'message': json.dumps(message_data),
            'src.name': GUPSHUP_CONFIG["app_name"]
        }
        
        # Make API call to Gupshup
        success, response_data, error_msg = make_gupshup_api_call(form_data)
        
        # Save outgoing message to database
        if success:
            save_outgoing_message_to_db(
                destination=destination_phone,
                message=reply_text,
                message_id=reply_message_id
            )
        
        return {
            "success": success,
            "message_id": reply_message_id,
            "response": response_data if success else error_msg
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def save_outgoing_message_to_db(destination, message, message_id):
    """Save outgoing message to database"""
    try:
        contact = get_or_create_contact(destination)
        
        message_doc = frappe.get_doc({
            "doctype": "WhatsApp Message",
            "source": GUPSHUP_CONFIG["source_number"],
            "destination": destination,
            "message": message,
            "message_id": message_id,
            "direction": "Outgoing",
            "message_type": "Text",
            "status": "Sent",
            "timestamp": datetime.now(),
            "contact": contact
        })
        
        message_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {"status": "success", "doc_name": message_doc.name}
        
    except Exception as e:
        frappe.log_error(f"Failed to save outgoing message: {str(e)}", "Outgoing Save Error")
        return {"status": "error", "message": str(e)}    


def process_and_reply_message(data):
    """Process incoming message, save to database, and send reply - FIXED VERSION"""
    try:
        # Extract message details with better error handling
        payload = data.get('payload', {})
        source_phone = payload.get('source', '')
        destination_phone = payload.get('destination', GUPSHUP_CONFIG["source_number"])
        
        # Better message content extraction
        message_payload = payload.get('payload', {})
        message_text = ""
        
        # Handle different message types
        msg_type = message_payload.get('type', 'text')
        if msg_type == 'text':
            message_text = message_payload.get('text', '').strip()
        else:
            message_text = f"Received {msg_type} message"
        
        # Fallback if no text found
        if not message_text:
            message_text = "Empty message received"
        
        message_id = payload.get('id', f"incoming_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}")
        
        # Clean phone numbers
        clean_source = clean_phone_number(source_phone)
        clean_destination = clean_phone_number(destination_phone)
        
        # Validate phone numbers
        if not clean_source:
            return {"status": "error", "message": "Invalid source phone number"}
        
        # 1. Save incoming message to database
        saved_message = save_incoming_message_to_db_fixed(
            source=clean_source,
            destination=clean_destination,
            message=message_text,
            message_id=message_id
        )
        
        # 2. Generate and send reply (only if database save was successful)
        reply_result = {"success": False, "message": "Skipped due to database error"}
        if saved_message.get("status") == "success":
            reply_text = generate_reply(message_text, clean_source)
            reply_result = send_reply_message_fixed(clean_source, reply_text)
        
        return {
            "status": "success",
            "message": "Message processed",
            "incoming_message": {
                "doc_name": saved_message.get("doc_name"),
                "source": clean_source,
                "text": message_text,
                "save_status": saved_message.get("status")
            },
            "reply_sent": {
                "success": reply_result.get("success"),
                "text": reply_text if saved_message.get("status") == "success" else "Not sent"
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Processing error: {str(e)}"}

def save_incoming_message_to_db_fixed(source, destination, message, message_id):
    """Fixed version of database save with better error handling"""
    try:
        # Validate inputs
        if not source or not message_id:
            return {"status": "error", "message": "Missing required fields"}
        
        # Check for duplicate messages
        existing = frappe.db.exists("WhatsApp Message", {"message_id": message_id})
        if existing:
            return {"status": "duplicate", "doc_name": existing}
        
        # Try to create contact first
        contact_name = None
        try:
            contact_name = get_or_create_contact_fixed(source)
        except Exception as contact_error:
            # Continue without contact if contact creation fails
            frappe.log_error(f"Contact creation failed: {str(contact_error)}", "Contact Error")
        
        # Create minimal WhatsApp Message document
        message_data = {
            "doctype": "WhatsApp Message",
            "message_id": message_id,
            "direction": "Incoming",
            "message_type": "Text",
            "status": "Delivered",
            "timestamp": datetime.now(),
            "message": message[:500]  # Truncate long messages
        }
        
        # Add phone numbers if they exist
        if source:
            message_data["source"] = source
        if destination:
            message_data["destination"] = destination
        if contact_name:
            message_data["contact"] = contact_name
        
        # Try to create the document
        message_doc = frappe.get_doc(message_data)
        message_doc.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.commit()
        
        return {
            "status": "success",
            "doc_name": message_doc.name
        }
        
    except Exception as e:
        error_msg = str(e)
        frappe.log_error(f"DB save failed: {error_msg}", "DB Save Error")
        return {"status": "error", "message": error_msg}

def get_or_create_contact_fixed(phone_number):
    """Fixed contact creation with better error handling"""
    try:
        if not phone_number:
            return None
            
        clean_phone = clean_phone_number(phone_number)
        
        # Try to find existing contact
        existing_contacts = frappe.get_all(
            "Whatsapp Contact",
            filters={"phone_number": clean_phone},
            fields=["name"],
            limit=1
        )
        
        if existing_contacts:
            return existing_contacts[0].name
        
        # Create new contact with minimal required fields
        contact_data = {
            "doctype": "Whatsapp Contact",
            "phone_number": clean_phone,
            "name1": f"Contact {clean_phone[-4:]}"  # Simple name
        }
        
        # Add optional fields safely
        try:
            contact_data["opt_in_status"] = "Opted In"
        except:
            pass
        
        contact_doc = frappe.get_doc(contact_data)
        contact_doc.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.commit()
        
        return contact_doc.name
        
    except Exception as e:
        # Return None if contact creation fails - don't break the whole process
        frappe.log_error(f"Contact creation error: {str(e)}", "Contact Error")
        return None

def send_reply_message_fixed(destination_phone, reply_text):
    """Fixed reply sending with better error handling"""
    try:
        if not destination_phone or not reply_text:
            return {"success": False, "error": "Missing destination or message"}
        
        # Generate message ID for the reply
        reply_message_id = f"reply_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Prepare message data for Gupshup
        message_data = {
            'type': 'text',
            'text': str(reply_text)[:1000]  # Truncate long messages
        }
        
        # Prepare form data for Gupshup API
        form_data = {
            'channel': 'whatsapp',
            'source': GUPSHUP_CONFIG["source_number"],
            'destination': destination_phone,
            'message': json.dumps(message_data),
            'src.name': GUPSHUP_CONFIG["app_name"]
        }
        
        # Make API call to Gupshup
        success, response_data, error_msg = make_gupshup_api_call(form_data)
        
        # Save outgoing message to database if API call was successful
        if success:
            try:
                save_outgoing_message_to_db_fixed(
                    destination=destination_phone,
                    message=reply_text,
                    message_id=reply_message_id
                )
            except Exception as save_error:
                # Don't fail the whole operation if database save fails
                frappe.log_error(f"Failed to save outgoing message: {str(save_error)}", "Outgoing Save Error")
        
        return {
            "success": success,
            "message_id": reply_message_id,
            "response": response_data if success else error_msg
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def save_outgoing_message_to_db_fixed(destination, message, message_id):
    """Fixed outgoing message save"""
    try:
        contact_name = get_or_create_contact_fixed(destination)
        
        message_data = {
            "doctype": "WhatsApp Message",
            "message_id": message_id,
            "direction": "Outgoing",
            "message_type": "Text",
            "status": "Sent",
            "timestamp": datetime.now(),
            "message": message[:500]
        }
        
        if GUPSHUP_CONFIG["source_number"]:
            message_data["source"] = GUPSHUP_CONFIG["source_number"]
        if destination:
            message_data["destination"] = destination
        if contact_name:
            message_data["contact"] = contact_name
        
        message_doc = frappe.get_doc(message_data)
        message_doc.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.commit()
        
        return {"status": "success", "doc_name": message_doc.name}
        
    except Exception as e:
        frappe.log_error(f"Failed to save outgoing message: {str(e)}", "Outgoing Save Error")
        return {"status": "error", "message": str(e)}        