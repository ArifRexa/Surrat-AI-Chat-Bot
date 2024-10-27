import os
import threading
import time
import json
import base64
from datetime import timedelta
from django.utils import timezone
# from html.parser import incomplete

import logging
from time import process_time
from pydub import AudioSegment
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from .models import AudioRequest, instruction_per_page, RequestCounter
# from channels.generic.websocket import SyncConsumer
from channels.consumer import SyncConsumer, AsyncConsumer

from .services.TTS import tts
from .services.ai_services import ProcessData
from .services.image_processing import encode_image, send_image_to_gpt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
User = get_user_model()

class MySyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        print("WebSocket connected...", event)
        self.send({
            'type': 'websocket.accept',
        })

    # def websocket_receive(self, event):
    #     print("WebSocket received...", event)
    #     try:
    #         if 'text' in event:
    #             data = json.loads(event['text'])
    #             page_number = data.get('page_number')
    #             user_email = data.get('email')
    #             audio_file_data = data.get('audio_file')
    #
    #             if isinstance(audio_file_data, str):
    #                 audio_bytes = base64.b64decode(audio_file_data)
    #                 file_name = f"sound_from_user{time.time()}.mp3"
    #                 audio_file_path = f'static/audio/{file_name}'
    #
    #                 # Create directory if it doesn't exist
    #                 os.makedirs('static/audio', exist_ok=True)
    #                 with open(audio_file_path, 'wb') as audio_file:
    #                     audio_file.write(audio_bytes)
    #
    #                 instruction = instruction_per_page.objects.get(page_number=page_number)
    #
    #                 process_data = ProcessData(user=data.get('id'))
    #                 processed_data = process_data.process_audio({
    #                     "audio_file": open(audio_file_path, 'rb'),
    #                     "instruction": instruction.instruction_text,
    #                 })
    #
    #                 if "error" in processed_data:
    #                     self.send({
    #                         'type': 'websocket.send',
    #                         'text': json.dumps({"error": processed_data["error"]})
    #                     })
    #                     return
    #
    #                 # processed_audio_filename = processed_data["filename"]
    #                 # audio_file_full_path = f'static/audio/{processed_audio_filename}'
    #
    #                 user = User.objects.get(email=user_email)
    #                 audio_request = AudioRequest(
    #                     user=user,
    #                     page_number=page_number,
    #                     instruction=instruction.instruction_text,
    #                     transcribed_text=processed_data["transcribed_text"],
    #                     translated_text=processed_data["translated_text"],
    #                     gpt_response=processed_data["gpt_response"],
    #                     translated_response=processed_data["translated_response"],
    #                 )
    #                 audio_request.audio.save(file_name, ContentFile(audio_bytes))
    #
    #                 # Save the request without response_audio
    #                 audio_request.save()
    #
    #                 # Send the first response (without response_audio)
    #                 self.send({
    #                     'type': 'websocket.send',
    #                     'text': json.dumps({"type": "incomplete", "data":{
    #                         "id": audio_request.id,
    #                         "transcribed_text": audio_request.transcribed_text,
    #                         "translated_text": audio_request.translated_text,
    #                         "gpt_response": audio_request.gpt_response,
    #                         "translated_response": audio_request.translated_response,
    #                         "audio": self.get_full_url(audio_request.audio.url) if audio_request.audio else None, #user given audio
    #                         "response_audio": None  # Initially no response audio
    #                     }})
    #                 })
    #
    #                 incomplete_response = {
    #                     "type": "incomplete",
    #                     "data":{
    #                         "id": audio_request.id,
    #                         "transcribed_text": audio_request.transcribed_text,
    #                         "translated_text": audio_request.translated_text,
    #                         "gpt_response": audio_request.gpt_response,
    #                         "translated_response": audio_request.translated_response,
    #                         "user_audio": self.get_full_url(audio_request.audio.url) if audio_request.audio else None,
    #                         "response_audio": None  # Initially no response audio
    #                     }
    #                 }
    #
    #                 print("First response:", json.dumps(incomplete_response, indent=4))
    #
    #                 timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format timestamp for readability
    #                 filename = f"Generated_Audio_nor_to_sami_{timestamp}.mp3"
    #
    #                 try:
    #                     # tts = self.tts.tts(translated_text, filename)
    #                     # from .TTS import tts
    #                     tts(audio_request.translated_response, filename)
    #
    #                 except Exception as e:
    #                     return {"error": f"Error during TTS generation: {str(e)}"}
    #
    #
    #                 # Function to send the second response after 10 seconds
    #                 def send_response_audio():
    #                     time.sleep(10)  # Wait for 10 seconds
    #                     audio_file_full_path = f'static/audio/{filename}'
    #
    #                     while not os.path.exists(audio_file_full_path):
    #                         time.sleep(5)
    #
    #                         # Ensure the file exists and save it
    #                     if os.path.exists(audio_file_full_path):
    #                         with open(audio_file_full_path, 'rb') as response_audio_file:
    #                             audio_request.response_audio.save(
    #                                 filename,
    #                                 ContentFile(response_audio_file.read())
    #                             )
    #                         audio_request.save()
    #
    #                         # Send the second response (with response_audio)
    #                         self.send({
    #                             'type': 'websocket.send',
    #                             'text': json.dumps({"type": "complete", "data":{
    #                                 "id": audio_request.id,
    #                                 "transcribed_text": audio_request.transcribed_text,
    #                                 "translated_text": audio_request.translated_text,
    #                                 "gpt_response": audio_request.gpt_response,
    #                                 "translated_response": audio_request.translated_response,
    #                                 "audio": self.get_full_url(audio_request.audio.url) if audio_request.audio else None, #user given audio
    #                                 "response_audio": self.get_full_url(audio_request.response_audio.url)  # Include the response audio now
    #                             }})
    #                         })
    #
    #                         complete_response = {
    #                             "type": "complete",
    #                             "data": {
    #                                 "id": audio_request.id,
    #                                 "transcribed_text": audio_request.transcribed_text,
    #                                 "translated_text": audio_request.translated_text,
    #                                 "gpt_response": audio_request.gpt_response,
    #                                 "translated_response": audio_request.translated_response,
    #                                 "user_audio": self.get_full_url(
    #                                     audio_request.audio.url) if audio_request.audio else None,
    #                                 "response_audio": self.get_full_url(audio_request.response_audio.url)  # Initially no response audio
    #                             }
    #                         }
    #
    #                         print("Final response:", json.dumps(complete_response, indent=4))
    #
    #                 # Start a new thread to delay and send the second response
    #                 threading.Thread(target=send_response_audio).start()
    #
    #             else:
    #                 self.send({
    #                     'type': 'websocket.send',
    #                     'text': json.dumps({'error': 'Audio file data is not a valid base64 string'})
    #                 })
    #
    #     except Exception as e:
    #         self.send({
    #             'type': 'websocket.send',
    #             'text': json.dumps({'error': f'An error occurred: {e}'})
    #         })
    #
    #
    # def get_full_url(self, relative_url):
    #     # Get the host and protocol from the WebSocket scope
    #     headers = dict((x.decode(), y.decode()) for x, y in self.scope['headers'])
    #     domain_name = headers.get('host')
    #     protocol = headers.get('x-forwarded-proto', 'http')  # Defaults to 'http' if not found
    #     return f'{protocol}://{domain_name}{relative_url}'

    def websocket_receive(self, event):
        logger.info("WebSocket received: %s", event)
        try:
            if 'text' in event:
                data = json.loads(event['text'])
                page_number = data.get('page_number')
                user_email = data.get('email')
                audio_file_data = data.get('audio_file')

                # Get the user
                user = User.objects.get(email=user_email)

                #============================== Giving 1 chance after each 5 minuts======================
                request_counter = RequestCounter.objects.filter(user=user, page_number=page_number).first()

                current_time = timezone.now()

                if request_counter.request_count >= 10:
                    # self.send_error(
                    #     "You have reached the maximum number of requests for today. Please try again after 5 minutes.")
                    max_level_response = {
                        "type": "max_imit_reached",
                        "data": {
                            "message": "You have reached the maximum number of requests for today. Please try again after 24hr."
                        }
                    }

                    self.send({
                        'type': 'websocket.send',
                        'text': json.dumps(max_level_response)
                    })
                    return

                # Proceed with audio processing
                if not isinstance(audio_file_data, str):
                    self.send_error("Audio file data is not a valid base64 string")
                    return

                audio_bytes = base64.b64decode(audio_file_data)
                file_name = f"sound_from_user{time.time()}.mp3"
                audio_file_path = self.save_audio_file(audio_bytes, file_name)

                # Get user audio duration
                user_audio_duration = self.get_audio_duration(audio_file_path)
                print(f"User audio duration: {user_audio_duration} seconds")

                instruction = self.get_instruction(page_number)
                print("*"*100)
                print("Thius is instructions: ", instruction.instruction_text)
                processed_data = self.process_audio(data, audio_file_path, instruction)

                if "error" in processed_data:
                    self.send_error(processed_data["error"])
                    return


                audio_request = self.create_audio_request(user, page_number, instruction, processed_data, file_name,
                                                          audio_bytes)

                self.send_initial_response(audio_request, user_audio_duration)
                flag = self.schedule_response_audio(audio_request, processed_data["translated_response"], user_audio_duration)
                if flag:
                    # Increment the request count for this request
                    request_counter.request_count += 1
                    request_counter.last_request_at = current_time  # Update last request time
                    # request_counter.updated_at = current_time  # Update last request time
                    request_counter.save()

        except Exception as e:
            self.send_error(f'An error occurred: {e}')

    def save_audio_file(self, audio_bytes, file_name):
        audio_file_path = f'static/audio/{file_name}'
        os.makedirs('static/audio', exist_ok=True)
        with open(audio_file_path, 'wb') as audio_file:
            audio_file.write(audio_bytes)
        return audio_file_path

    def get_instruction(self, page_number):
        return instruction_per_page.objects.get(page_number=page_number)

    def process_audio(self, data, audio_file_path, instruction):
        process_data = ProcessData(user=data.get('id'))

        if instruction.instruction_image:
            base64_image = encode_image(instruction.instruction_image)
            # gpt_response = send_image_to_gpt(base64_image, instruction.instruction_text)
            print("@" * 100)
            # gpt_text = f"\nGPT Response: {gpt_response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
            # print("GPT Response:", gpt_text)
            return process_data.process_audio({
                "audio_file": open(audio_file_path, 'rb'),
                "instruction": instruction.instruction_text,
                "instruction_image": base64_image,

            })

        else:
            print("#" * 100)
            return process_data.process_audio({
                "audio_file": open(audio_file_path, 'rb'),
                "instruction": instruction.instruction_text,
            })

    def create_audio_request(self, user, page_number, instruction, processed_data, file_name, audio_bytes):
        audio_request = AudioRequest(
            user=user,
            page_number=page_number,
            instruction=instruction.instruction_text,
            transcribed_text=processed_data["transcribed_text"],
            translated_text=processed_data["translated_text"],
            gpt_response=processed_data["gpt_response"],
            translated_response=processed_data["translated_response"],
        )
        audio_request.audio.save(file_name, ContentFile(audio_bytes))
        audio_request.save()
        return audio_request

    def send_initial_response(self, audio_request, user_audio_duration):
        incomplete_response = {
            "type": "incomplete",
            "data": {
                "id": audio_request.id,
                "transcribed_text": audio_request.transcribed_text,
                "translated_text": audio_request.translated_text,
                "gpt_response": audio_request.gpt_response,
                "translated_response": audio_request.translated_response,
                "audio": self.get_full_url(audio_request.audio.url),
                "audio_duration": user_audio_duration,
                "response_audio": None,
            }
        }
        self.send({
            'type': 'websocket.send',
            'text': json.dumps(incomplete_response)
        })
        print("First response sent: %s", json.dumps(incomplete_response, indent=4))
        logger.info("First response sent: %s", json.dumps(incomplete_response, indent=4))

    def schedule_response_audio(self, audio_request, translated_response, user_audio_duration):
        def send_response_audio():
            time.sleep(10)  # Wait for 10 seconds
            filename = self.generate_audio_filename()
            self.generate_tts_audio(translated_response, filename)

            audio_file_full_path = f'static/audio/{filename}'
            while not os.path.exists(audio_file_full_path):
                time.sleep(5)

            if os.path.exists(audio_file_full_path):
                self.save_and_send_response_audio(audio_request, filename, user_audio_duration)

        threading.Thread(target=send_response_audio).start()
        return True

    def generate_audio_filename(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return f"Generated_Audio_nor_to_sami_{timestamp}.mp3"

    def generate_tts_audio(self, translated_response, filename):
        try:
            tts(translated_response, filename)
        except Exception as e:
            logger.error("Error during TTS generation: %s", str(e))
            print("Error during TTS generation: %s", str(e))
            self.send_error(f"Error during TTS generation: {str(e)}")

    def save_and_send_response_audio(self, audio_request, filename, user_audio_duration):
        audio_file_full_path = f'static/audio/{filename}'
        with open(audio_file_full_path, 'rb') as response_audio_file:
            audio_request.response_audio.save(filename, ContentFile(response_audio_file.read()))
        audio_request.save()
        # Get user audio duration
        response_audio_duration = self.get_audio_duration(audio_file_full_path)
        print(f"Response audio duration: {response_audio_duration} seconds")

        complete_response = {
            "type": "complete",
            "data": {
                "id": audio_request.id,
                "transcribed_text": audio_request.transcribed_text,
                "translated_text": audio_request.translated_text,
                "gpt_response": audio_request.gpt_response,
                "translated_response": audio_request.translated_response,
                "audio": self.get_full_url(audio_request.audio.url),
                "audio_duration": user_audio_duration,
                "response_audio": self.get_full_url(audio_request.response_audio.url),
                "response_audio_duration": response_audio_duration,
            }
        }
        self.send({
            'type': 'websocket.send',
            'text': json.dumps(complete_response)
        })
        print("Final response sent: %s", json.dumps(complete_response, indent=4))
        logger.info("Final response sent: %s", json.dumps(complete_response, indent=4))

    def send_error(self, message):
        self.send({
            'type': 'websocket.send',
            'text': json.dumps({'error': message})
        })

    def get_full_url(self, relative_url):
        headers = dict((x.decode(), y.decode()) for x, y in self.scope['headers'])
        protocol = headers.get('x-forwarded-proto', 'http')
        domain_name = headers.get('host')
        return f'{protocol}://{domain_name}{relative_url}'

    def get_audio_duration(self, file_path):
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000  # duration in seconds


    def websocket_disconnect(self, event):
        print("WebSocket disconnected...", event)




class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("WebSocket connected...", event)

    async def websocket_receive(self, event):
        print("WebSocket received...", event)

    async def websocket_disconnect(self, event):
        print("WebSocket disconnected...", event)

