import logging
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from xmpp import Client, Iq, Presence, Message
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="XMPP Message Sender")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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
credentials = []

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Serve the index.html from static directory
    with open('static/index.html', 'r') as f:
        return HTMLResponse(content=f.read())

@app.post("/send-xmpp-message")
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
        if not client.auth(username, payload.fromJIDPass, resource=resource):
            raise HTTPException(
                status_code=401, 
                detail="Authentication failed"
            )
        
        # Send initial presence
        client.sendInitPresence()
        
        # Create and send message
        msg = Message(payload.toJID, payload.message)
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
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run the server with: 
# uvicorn main:app --reload