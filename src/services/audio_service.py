import speech_recognition as sr
from typing import Optional
import requests
import tempfile
import os

class AudioService:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    async def convert_audio_to_text(self, audio_url: str) -> Optional[str]:
        """Convert WhatsApp audio message to text"""
        try:
            # Download the audio file
            audio_data = requests.get(audio_url)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_audio:
                temp_audio.write(audio_data.content)
                temp_audio_path = temp_audio.name

            # Convert audio to text
            with sr.AudioFile(temp_audio_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)  # Using Google's speech recognition

            # Clean up temporary file
            os.unlink(temp_audio_path)
            
            return text

        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return None 