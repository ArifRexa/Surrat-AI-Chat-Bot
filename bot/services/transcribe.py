import requests
import os
from dotenv import load_dotenv

load_dotenv()


class Transcriber:
    def __init__(self, api_key=None, model_url=None, language="en"):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable is not set")

        self.api_url = (
            model_url
            or "https://api-inference.huggingface.co/models/NbAiLab/whisper-large-sme"
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "language": language,
        }

    def transcribe_voice(self, audio_data):
        response = requests.post(self.api_url, headers=self.headers, data=audio_data)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        transcription = response.json()
        print(f"From the transcription class: {transcription}")

        if "text" not in transcription:
            raise ValueError(
                'Transcription failed: "text" key is missing in the response'
            )

        return transcription["text"]
