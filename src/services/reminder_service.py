from datetime import datetime
from typing import Dict, List, Optional
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from ..utils.config import get_settings

settings = get_settings()

class ReminderService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.reminders: Dict[str, Dict] = {}
        self.scheduler.start()

    async def create_reminder(self, task: str, reminder_time: datetime) -> str:
        """Create a new reminder"""
        reminder_id = f"reminder_{len(self.reminders) + 1}"
        
        reminder = {
            'id': reminder_id,
            'task': task,
            'time': reminder_time,
            'status': 'scheduled'
        }
        
        self.reminders[reminder_id] = reminder
        
        # Schedule the reminder
        self.scheduler.add_job(
            self._trigger_reminder,
            'date',
            run_date=reminder_time,
            args=[reminder_id],
            id=reminder_id
        )
        
        return reminder_id

    async def _trigger_reminder(self, reminder_id: str):
        """Trigger the reminder when it's time"""
        reminder = self.reminders.get(reminder_id)
        if reminder:
            reminder['status'] = 'triggered'
            # Here you would implement the actual reminder notification
            # For example, sending a WhatsApp message
            await self._send_reminder_notification(reminder)
            
            # Auto-delete if configured
            if settings.AUTO_DELETE_MESSAGES:
                await self._cleanup_reminder(reminder_id)

    async def _send_reminder_notification(self, reminder: Dict):
        """Send the reminder notification via WhatsApp"""
        # Implementation for sending WhatsApp message will go here
        message = f"🔔 Reminder: {reminder['task']}"
        print(f"Sending reminder: {message}")  # Placeholder for actual implementation

    async def _cleanup_reminder(self, reminder_id: str):
        """Clean up the reminder after it's triggered"""
        if reminder_id in self.reminders:
            del self.reminders[reminder_id]
            try:
                self.scheduler.remove_job(reminder_id)
            except:
                pass

    async def get_pending_reminders(self) -> List[Dict]:
        """Get all pending reminders"""
        return [
            reminder for reminder in self.reminders.values()
            if reminder['status'] == 'scheduled'
        ]

    async def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancel a scheduled reminder"""
        if reminder_id in self.reminders:
            await self._cleanup_reminder(reminder_id)
            return True
        return False 