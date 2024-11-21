# XMPP Connection Server

## Features
- REST API endpoint for XMPP connections
- WebSocket support for real-time XMPP operations
- Simple authentication and message sending

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

### POST /connect
Send XMPP connection credentials and send a message

#### Request Body
```json
{
    "username": "your_username",
    "password": "your_password", 
    "server": "xmpp_server_address",
    "port": 5222,
    "target": "optional_target_user"
}
```

### WebSocket /ws/xmpp
Real-time XMPP connection and messaging

## Notes
- Disable SSL verification for local/testing environments
- Supports both REST and WebSocket connections
