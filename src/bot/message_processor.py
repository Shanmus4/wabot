from datetime import datetime, timedelta
import re
from typing import Dict, Optional, Tuple
from ..services.nlp_service import NLPService
from ..services.reminder_service import ReminderService
from ..services.audio_service import AudioService

class MessageProcessor:
    def __init__(self):
        self.nlp_service = NLPService()
        self.reminder_service = ReminderService()
        self.audio_service = AudioService()

    async def process_message(self, message: Dict) -> str:
        """Process incoming WhatsApp messages"""
        try:
            if message.get('type') == 'audio':
                # Convert audio to text
                text = await self.audio_service.convert_audio_to_text(message['audio_url'])
            else:
                text = message.get('text', '')

            # Process the message text
            intent, entities = await self.nlp_service.analyze_text(text)
            
            if intent == 'set_reminder':
                return await self._handle_reminder(entities)
            elif intent == 'help':
                return self._get_help_message()
            else:
                return "I'm not sure what you want. Try asking for help by saying 'help'!"

        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    async def _handle_reminder(self, entities: Dict) -> str:
        """Handle reminder creation"""
        task = entities.get('task')
        time = entities.get('time')
        
        if not task or not time:
            return "Please specify what and when you want to be reminded about."
        
        reminder_id = await self.reminder_service.create_reminder(task, time)
        return f"✅ I'll remind you to {task} at {time}."

    def _get_help_message(self) -> str:
        return """
        🤖 WhatsApp Reminder Bot Help:
        
        You can:
        1. Set a reminder by saying something like:
           - "remind me to call John in 5 minutes"
           - "set a reminder for meeting tomorrow at 2pm"
        
        2. Send voice messages with the same commands
        
        3. Type 'help' anytime to see this message again
        """ 