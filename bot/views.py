import base64
import time
from datetime import datetime, timedelta
import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
import os
from rest_framework import generics
from users.models import ChatHistory
from .models import instruction_per_page, AudioRequest, RequestCounter
from .services.ai_services import AIService, ProcessData
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from bot.serializers import (
    AudioFileSerializer,
    TranslationSerializer,
    TranscriptSerializer,
    AudioRequestSerializer, UsersAllAudioRequestSerializer, RequestCounterSerializer,
)
from subscriptions.permissions import HasActiveSubscription
from bot.services.translate import Translator
from .services.transcribe import Transcriber

# Create your views here.
logger = logging.getLogger(__name__)
ai_service = AIService()
User = get_user_model()

class ProcessAudio(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = AudioFileSerializer

    def post(self, request, *args, **kwargs):
        serializer = AudioFileSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data["file"]
            target_lang = serializer.validated_data.get("lang", "sme")
            # chatgpt_prompt = serializer.validated_data.get('prompt', None)

            if file.name.lower().endswith((".mp3", ".wav")):
                audio_data = file.read()
                filename = f"Generated_Audio_{target_lang}_{time.time()}.mp3"
                result = ai_service.process_audio(audio_data, filename)
                print(result)
                if "error" in result:
                    return JsonResponse(result, status=400)

                ChatHistory.objects.create(
                    user=request.user,
                    user_message=result,
                    bot_reply=result["translated_chat_response"],
                )

                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Unsupported file format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Translate(APIView):
    serializer_class = TranslationSerializer
    permission_classes = [
        IsAuthenticated,
        HasActiveSubscription,
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data["text"]
            source_language = serializer.validated_data["source_language"]
            target_language = serializer.validated_data["target_language"]
            translation_object = Translator()
            response = translation_object.perform_translation(
                text=text, src_lang=source_language, tgt_lang=target_language
            )
            return Response({"response": response}, status=status.HTTP_200_OK)


class Transcript(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = TranscriptSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        transcript_object = Transcriber()

        try:
            response = transcript_object.transcribe_voice(audio_data=file.read())
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return JsonResponse({"data": response}, status=status.HTTP_200_OK)
import requests
# # def encode_image(image_path):
# def encode_image(image_file):
#
#     return base64.b64encode(image_file.read()).decode('utf-8')
#     # with open(image_path, "rb") as image_file:
#     #     return base64.b64encode(image_file.read()).decode('utf-8')
# def send_image_to_gpt(base64_image, text):
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
#     }
#     payload = {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": f"{text}"
#                     },
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ],
#         "max_tokens": 300
#     }
#     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
#     return response.json()
class AudioRequestView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    serializer_class = AudioRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Save the initial request with the authenticated user
            print("requested user id: ", request.user.id)
            print("This is request dot user: ", request.user)
            audio_request = serializer.save(user=request.user)
            print(audio_request.page_number)
            instruction = instruction_per_page.objects.get(page_number=audio_request.page_number)
            audio_request.instruction = instruction.instruction_text
            print(instruction.instruction_text)

            # Process the audio and related data
            process_data = ProcessData(user=request.user)
            processed_data = process_data.process_audio(
                {
                    "audio_file": audio_request.audio,
                    "instruction": instruction.instruction_text,
                }
            )
            print("This is process data: ", processed_data)

            # Check for errors in the processing steps
            if "error" in processed_data:
                return Response(
                    {"error": processed_data["error"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the model with the results
            audio_request.transcribed_text = processed_data["transcribed_text"]
            audio_request.translated_text = processed_data["translated_text"]
            audio_request.gpt_response = processed_data["gpt_response"]
            audio_request.translated_response = processed_data["translated_response"]
            # audio_request.response_audio = processed_data["filename"]
            audio_request.save()

            return Response(
                AudioRequestSerializer(audio_request).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ========================upper one working==========================
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
#
# class AudioRequestView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [IsAuthenticated]
#     serializer_class = AudioRequestSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             audio_request = serializer.save(user=request.user)
#             instruction = instruction_per_page.objects.get(page_number=audio_request.page_number)
#             audio_request.instruction = instruction.instruction_text
#
#             process_data = ProcessData(user=request.user)
#             processed_data = process_data.process_audio(
#                 {
#                     "audio_file": audio_request.audio,
#                     "instruction": instruction.instruction_text,
#                 }
#             )
#
#             if "error" in processed_data:
#                 return Response(
#                     {"error": processed_data["error"]},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             audio_request.transcribed_text = processed_data["transcribed_text"]
#             audio_request.translated_text = processed_data["translated_text"]
#             audio_request.gpt_response = processed_data["gpt_response"]
#             audio_request.translated_response = processed_data["translated_response"]
#             audio_request.response_audio = processed_data["filename"]
#             audio_request.save()
#
#             # Send a message to the WebSocket group
#             channel_layer = get_channel_layer()
#             async_to_sync(channel_layer.group_send)(
#                 f"{request.user.id}_{audio_request.page_number}",
#                 {
#                     'type': 'audio_processing_complete',
#                     'message': 'Audio processing completed',
#                     'file_url': f"/static/audio/{processed_data['filename']}"
#                 }
#             )
#
#             return Response(
#                 AudioRequestSerializer(audio_request).data,
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AudioRequestListView(generics.ListAPIView):
    # parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    serializer_class = UsersAllAudioRequestSerializer

    def get_queryset(self):
        email = self.request.query_params.get('email')
        page_number = self.request.query_params.get('page_number')

        # if not email or not page_number:
        #     raise ValidationError("Both 'email' and 'page_number' query parameters are required.")

        queryset = AudioRequest.objects.filter(user__email=email, page_number=page_number)
        queryset = queryset.order_by('-created_at')
        return queryset

    # def get(self, request, *args, **kwargs):
    #     email = request.query_params.get('email')
    #     page_number = request.query_params.get('page_number')
    #
    #     if not email or not page_number:
    #         return Response({'detail': 'Email and page_number are required.'}, status=400)
    #
    #     try:
    #         audio_requests = AudioRequest.objects.filter(user__email=email, page_number=page_number)
    #         if not audio_requests.exists():
    #             raise 'No audio requests found for the provided email and page_number.'
    #
    #         serializer = self.get_serializer(audio_requests, many=True)
    #         return Response(serializer.data)
    #     except Exception as e:
    #         return Response({'detail': str(e)}, status=500)




class AudioRequestCountView(APIView):
    serializer_class = RequestCounterSerializer
    permission_classes = [IsAuthenticated]  # Ensures the user is authenticated

    # def post(self, request):
    #     page_number = request.data.get('page_number')
    #
    #     # Ensure that page_number is provided
    #     if not page_number:
    #         return Response({"error": "page_number is required."}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     # Get or create a RequestCounter object for the user and page number
    #     request_counter, created = RequestCounter.objects.get_or_create(
    #         user=request.user,
    #         page_number=page_number
    #     )
    #
    #     # If this is not a new entry, calculate how many days have passed since the last request
    #     if not created:
    #         now = timezone.now()  # Use timezone-aware datetime
    #         print(now)
    #         last_request_at = request_counter.last_request_at
    #         print(last_request_at)
    #         updated_at = request_counter.updated_at.date()
    #         print(updated_at)
    #         if updated_at != now.date():
    #
    #             if last_request_at.tzinfo is None:  # If last_request_at is naive
    #                 last_request_at = timezone.make_aware(last_request_at)  # Convert to aware
    #
    #             days_elapsed = (now - last_request_at).days
    #             print("Days elapsed:", days_elapsed)
    #
    #             # Decrease request_count by days_elapsed, but not below 0
    #             new_request_count = max(request_counter.request_count - days_elapsed, 0)
    #
    #             # Update request_count and last_request_at
    #             request_counter.request_count = new_request_count
    #             request_counter.updated_at = now
    #             # request_counter.last_request_at = now
    #             request_counter.save()
    #     else:
    #         # If created, initialize request_count
    #         request_counter.request_count = 1
    #         request_counter.last_request_at = timezone.now()
    #         request_counter.save()
    #
    #     print(f"Request count for page {page_number} is {request_counter.request_count}")
    #
    #     # Serialize the data using the serializer class
    #     serializer = self.serializer_class(request_counter)
    #
    #     # Return the response with the serialized data
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request):
        page_number = request.query_params.get('page_number')
        print(page_number)

        # Ensure that page_number is provided
        if not page_number:
            return Response({"error": "page_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create a RequestCounter object for the user and page number
        request_counter, created = RequestCounter.objects.get_or_create(
            user=request.user,
            page_number=page_number
        )

        # If this is not a new entry, calculate how many days have passed since the last request
        if not created:
            now = timezone.now()  # Use timezone-aware datetime
            print("Now: ", now)
            last_request_at = request_counter.last_request_at
            print("Last: ", last_request_at)
            updated_at = request_counter.updated_at
            print("Update", updated_at)
            if updated_at.date() != now.date():

                if last_request_at.tzinfo is None:  # If last_request_at is naive
                    last_request_at = timezone.make_aware(updated_at)  # Convert to aware

                days_elapsed = (now - updated_at).days
                print("Days elapsed:", days_elapsed)
                if days_elapsed != 0:

                    # Decrease request_count by days_elapsed, but not below 0
                    new_request_count = max(request_counter.request_count - days_elapsed, 0)

                    # Update request_count and last_request_at
                    request_counter.request_count = new_request_count
                    request_counter.updated_at = now
                    # request_counter.last_request_at = now
                    request_counter.save()
        else:
            # If created, initialize request_count
            request_counter.request_count = 1
            request_counter.last_request_at = timezone.now()
            request_counter.save()

        print(f"Request count for page {page_number} is {request_counter.request_count}")

        # Serialize the data using the serializer class
        serializer = self.serializer_class(request_counter)

        # Return the response with the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)









# ==========================Below this is the image for instruction ==================================
# class AudioRequestView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
#     serializer_class = AudioRequestSerializer
#
#     def post(self, request, *args, **kwargs):
#         serializer = AudioRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             # Save the initial request with the authenticated user
#             audio_request = serializer.save(user=request.user)
#             print(audio_request.page_number)
#
#             try:
#                 instruction = instruction_per_page.objects.get(page_number=audio_request.page_number)
#             except instruction_per_page.DoesNotExist:
#                 return Response(
#                     {"error": "Instruction not found for the given page number"},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )
#
#             instruction_text = instruction.instruction_text
#             instruction_image = instruction.instruction_image
#
#             # Prepare the image for GPT if it exists
#             if instruction_image:
#                 base64_image = encode_image(instruction.instruction_image)
#                 gpt_response = send_image_to_gpt(base64_image, instruction_text)
#                 instruction_text += f"\nGPT Response: {gpt_response.get('choices', [{}])[0].get('message', {}).get('content', '')}"
#                 print("GPT Response:", instruction_text)
#
#             # Process the audio and related data
#             process_data = ProcessData(user=request.user)
#             processed_data = process_data.process_audio(
#                 {
#                     "audio_file": audio_request.audio,
#                     "instruction": instruction_text,
#                 }
#             )
#             print("This is process data: ", processed_data)
#
#             # Check for errors in the processing steps
#             if "error" in processed_data:
#                 return Response(
#                     {"error": processed_data["error"]},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#
#             # Update the model with the results
#             audio_request.transcribed_text = processed_data.get("transcribed_text", "")
#             audio_request.translated_text = processed_data.get("translated_text", "")
#             audio_request.gpt_response = processed_data.get("gpt_response", "")
#             audio_request.translated_response = processed_data.get("translated_response", "")
#             audio_request.save()
#
#             return Response(
#                 # AudioRequestSerializer(audio_request).data,
#                 {
#                     "transcribed_text": audio_request.transcribed_text,
#                     "translated_text": audio_request.translated_text,
#                     "gpt_response": audio_request.gpt_response,
#                     "translated_response": audio_request.translated_response,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
