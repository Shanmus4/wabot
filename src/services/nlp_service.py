from transformers import pipeline
from typing import Dict, Tuple
import re
from datetime import datetime, timedelta

class NLPService:
    def __init__(self):
        self.classifier = pipeline("text-classification", model="bert-base-uncased")
        
    async def analyze_text(self, text: str) -> Tuple[str, Dict]:
        """Analyze text to determine intent and extract entities"""
        text = text.lower()
        
        # Simple rule-based intent classification
        if any(word in text for word in ['remind', 'reminder', 'schedule']):
            intent = 'set_reminder'
            entities = self._extract_reminder_entities(text)
        elif 'help' in text:
            intent = 'help'
            entities = {}
        else:
            intent = 'unknown'
            entities = {}
            
        return intent, entities
    
    def _extract_reminder_entities(self, text: str) -> Dict:
        """Extract task and time entities from reminder text"""
        # Basic time patterns
        time_patterns = {
            r'in (\d+) (minute|minutes|min|mins)': lambda x: datetime.now() + timedelta(minutes=int(x)),
            r'in (\d+) (hour|hours|hr|hrs)': lambda x: datetime.now() + timedelta(hours=int(x)),
            r'tomorrow at (\d+)(?::(\d+))?\s*(am|pm)?': self._parse_tomorrow_time,
            r'at (\d+)(?::(\d+))?\s*(am|pm)?': self._parse_today_time,
        }
        
        # Extract time
        time_str = None
        for pattern, time_func in time_patterns.items():
            match = re.search(pattern, text)
            if match:
                time_str = time_func(*match.groups())
                break
        
        # Extract task (everything before time indicator)
        task = re.split(r'\s+(?:in|at|tomorrow)\s+', text)[0]
        task = re.sub(r'^(?:remind me to|remind me|reminder to|reminder)\s+', '', task)
        
        return {
            'task': task.strip(),
            'time': time_str
        }
    
    def _parse_tomorrow_time(self, hour: str, minute: str = None, meridiem: str = None) -> datetime:
        """Parse time for tomorrow"""
        return self._parse_time(hour, minute, meridiem, is_tomorrow=True)
    
    def _parse_today_time(self, hour: str, minute: str = None, meridiem: str = None) -> datetime:
        """Parse time for today"""
        return self._parse_time(hour, minute, meridiem, is_tomorrow=False)
    
    def _parse_time(self, hour: str, minute: str = None, meridiem: str = None, is_tomorrow: bool = False) -> datetime:
        """Helper function to parse time"""
        hour = int(hour)
        minute = int(minute) if minute else 0
        
        if meridiem:
            if meridiem.lower() == 'pm' and hour < 12:
                hour += 12
            elif meridiem.lower() == 'am' and hour == 12:
                hour = 0
                
        now = datetime.now()
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if is_tomorrow:
            target_time += timedelta(days=1)
            
        return target_time 