from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .message_processor import MessageProcessor
from ..utils.config import get_settings
import uvicorn
import hmac
import hashlib
import json

app = FastAPI()
settings = get_settings()
message_processor = MessageProcessor()

def verify_whatsapp_signature(request: Request) -> bool:
    """Verify that the request is coming from WhatsApp"""
    signature = request.headers.get('X-Hub-Signature-256', '')
    if not signature:
        return False
    
    expected_signature = hmac.new(
        settings.WHATSAPP_API_SECRET.encode(),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, f"sha256={expected_signature}")

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming WhatsApp webhook requests"""
    if not verify_whatsapp_signature(request):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    body = await request.json()
    
    # Handle WhatsApp verification challenge
    if body.get("hub.mode") == "subscribe" and body.get("hub.challenge"):
        return JSONResponse(content=body["hub.challenge"])
    
    try:
        # Process the message
        messages = body.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
        
        if not messages:
            return JSONResponse(content={"status": "no message"})
        
        message = messages[0]
        response = await message_processor.process_message(message)
        
        # Send response back to WhatsApp
        # Implementation of sending message back to WhatsApp will go here
        
        return JSONResponse(content={"status": "processed"})
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    uvicorn.run("whatsapp_handler:app", host="0.0.0.0", port=8000, reload=True) 