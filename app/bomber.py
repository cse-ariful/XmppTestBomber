from typing import Optional
from fastapi import APIRouter
import logging
import json
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from xmpp import Client, Message
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
router = APIRouter()
# Mount static files

# Pydantic model for request payload
class XMPPPayload(BaseModel):
    serverUrl: str
    fromJID: str
    fromJIDPass: str
    toJID: str
    message: str

class CredentialPayload(BaseModel):
    username: str
    password: str

# Store credentials (in a real-world scenario, use a more secure storage)
credentials = [
    CredentialPayload(username="bob@localhost", password="admin"),
    CredentialPayload(username="tahsan@localhost", password="admin"),
    CredentialPayload(username="8801869946417@localhost", password="admin"),
    CredentialPayload(username="8801516157495@localhost", password="admin")
]

@router.get("/", response_class=HTMLResponse)
async def serve_index():
    # Serve the index.html from static directory
    with open('frontend/index.html', 'r') as f:
        return HTMLResponse(content=f.read())
# Helper function to find a credential by username
def find_credential(username: str) -> Optional[CredentialPayload]:
    return next((cred for cred in credentials if cred.username == username), None)

# POST endpoint to add a credential
@router.post("/credentials")
async def add_credential(credential: CredentialPayload):
    # Check if credential already exists
    if find_credential(credential.username):
        raise HTTPException(status_code=400, detail="Credential already exists")
    
    # Add the new credential
    credentials.append(credential)
    return {"message": f"Credential for {credential.username} added successfully"}

# DELETE endpoint to remove a credential
@router.delete("/credentials/{username}")
async def remove_credential(username: str):
    # Find and remove the credential
    existing_credential = find_credential(username)
    if not existing_credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    credentials.remove(existing_credential)
    return {"message": f"Credential for {username} removed successfully"}

# Endpoint to get the list of all credentials (for verification)
@router.get("/credentials")
async def get_credentials():
    return credentials


@router.post("/send-xmpp-message")
async def send_xmpp_message(payload: XMPPPayload):
    try:
        # More robust JID parsing
        def parse_jid(jid):
            # Split JID into parts (username, domain, resource)
            parts = jid.split('@')
            if len(parts) < 2:
                raise ValueError(f"Invalid JID format: {jid}")
            
            username = parts[0]
            domain_parts = parts[1].split('/')
            domain = domain_parts[0]
            
            # Resource is optional
            resource = domain_parts[1] if len(domain_parts) > 1 else username
            
            return username, domain, resource

        # Parse sender JID
        username, domain, resource = parse_jid(payload.fromJID)
        
        # Create XMPP client
        full_jid = f"{username}@{domain}/{resource}"
        client = Client(domain, debug=[])
        
        # Connect to the server
        if not client.connect(server=(payload.serverUrl, 5222)):
            raise HTTPException(
                status_code=400, 
                detail="Could not connect to XMPP server"
            )
        
        # Authenticate
        if not client.auth(username, payload.fromJIDPass):
            raise HTTPException(
                status_code=401, 
                detail="Authentication failed"
            )
        
        # Send initial presence
        client.sendInitPresence()
        
        # Create and send message
        message_id = str(uuid.uuid4())

        # Create the message with the necessary attributes
        msg = Message(payload.toJID, payload.message)
        msg.setAttr('type', 'chat')  # Set message type to 'chat'
        msg.setAttr('id', message_id)  # Set the message ID to a UUID

        # Send the message
        client.send(msg)
        
        # Disconnect
        client.disconnect()
        
        return {
            "status": "success", 
            "message": "XMPP message sent successfully"
        }
    
    except ValueError as ve:
        logger.error(f"JID parsing error: {str(ve)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid JID format: {str(ve)}"
        )
    except Exception as e:
        logger.error(f"XMPP message send error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error sending XMPP message: {str(e)}"
        )

# ... (rest of the code remains the same as in the previous version)

# Optional: Add a health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the server with: 
# uvicorn main:app --reload