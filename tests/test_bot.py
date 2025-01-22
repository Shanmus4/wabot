import pytest
from datetime import datetime, timedelta
from src.services.nlp_service import NLPService
from src.services.reminder_service import ReminderService
from src.bot.message_processor import MessageProcessor

@pytest.mark.asyncio
async def test_nlp_service():
    nlp = NLPService()
    text = "remind me to call John in 5 minutes"
    intent, entities = await nlp.analyze_text(text)
    
    assert intent == "set_reminder"
    assert "task" in entities
    assert "time" in entities
    assert "call John" in entities["task"].lower()

@pytest.mark.asyncio
async def test_reminder_service():
    reminder = ReminderService()
    task = "Test reminder"
    reminder_time = datetime.now() + timedelta(minutes=5)
    
    reminder_id = await reminder.create_reminder(task, reminder_time)
    assert reminder_id is not None
    
    pending = await reminder.get_pending_reminders()
    assert len(pending) > 0
    
    success = await reminder.cancel_reminder(reminder_id)
    assert success is True

@pytest.mark.asyncio
async def test_message_processor():
    processor = MessageProcessor()
    message = {
        "type": "text",
        "text": "help"
    }
    
    response = await processor.process_message(message)
    assert "WhatsApp Reminder Bot Help" in response 