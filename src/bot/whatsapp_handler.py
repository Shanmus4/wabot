from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from .message_processor import MessageProcessor
from ..utils.config import get_settings
import uvicorn
import hmac
import hashlib
import json
import aiohttp

app = FastAPI()
settings = get_settings()
message_processor = MessageProcessor()


@app.get("/webhook")
async def verify_webhook(
    request: Request,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Handle webhook verification from Meta"""
    print("=== Webhook Verification Debug ===")
    print(f"Received mode: {hub_mode}")
    print(f"Received token: {hub_verify_token}")
    print(f"Received challenge: {hub_challenge}")
    print(f"Expected token: {settings.WHATSAPP_API_SECRET}")
    print("================================")

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_API_SECRET:
        print("✅ Verification successful!")
        if hub_challenge:
            return PlainTextResponse(content=str(hub_challenge))
        return PlainTextResponse(content="OK")

    print("❌ Verification failed!")
    print(f"Token match: {hub_verify_token == settings.WHATSAPP_API_SECRET}")
    raise HTTPException(status_code=403, detail="Verification failed")


async def send_whatsapp_message(to: str, message: str):
    """Send WhatsApp message using the Cloud API"""
    url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_NUMBER}/messages"

    print("\n=== Sending WhatsApp Message ===")
    print(f"To: {to}")
    print(f"Message: {message}")
    print(f"URL: {url}")
    print(f"Phone Number ID: {settings.WHATSAPP_PHONE_NUMBER}")

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }

    print("\nRequest Data:")
    print(json.dumps(data, indent=2))

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response_data = await response.json()
                print("\nResponse Status:", response.status)
                print("Response Data:")
                print(json.dumps(response_data, indent=2))
                return response_data
    except Exception as e:
        print(f"\nError sending message: {str(e)}")
        raise


@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming WhatsApp webhook requests"""
    body = await request.json()
    print("\n=== Received Webhook ===")
    print(json.dumps(body, indent=2))

    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            print("No messages found in webhook")
            return JSONResponse(content={"status": "no message"})

        message = messages[0]
        sender = message.get("from")
        print(f"\nSender: {sender}")
        print(f"Message: {message}")

        response = await message_processor.process_message(message)
        print(f"\nBot Response: {response}")

        if response:
            print("\nAttempting to send response...")
            await send_whatsapp_message(sender, response)
            print("Response sent successfully")

        return JSONResponse(content={"status": "processed"})

    except Exception as e:
        print(f"\nError processing webhook: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run("src.bot.whatsapp_handler:app", host="0.0.0.0", port=8000, reload=True)
