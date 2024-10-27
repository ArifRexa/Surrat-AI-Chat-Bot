from rest_framework import serializers
from django.core.exceptions import ValidationError
import mimetypes
from bot.models import AudioRequest, RequestCounter


class AudioFileSerializer(serializers.Serializer):
    file = serializers.FileField()
    lang = serializers.CharField(max_length=10, default="sme", required=False)

    def validate_file(self, value):
        # Validate the file's MIME type to ensure it's an audio file
        mime_type, encoding = mimetypes.guess_type(value.name)
        if not mime_type or not mime_type.startswith("audio"):
            raise ValidationError("Invalid file type. Only audio files are allowed.")
        return value

    # prompt = serializers.CharField(max_length=255, required=False)


class TranslationSerializer(serializers.Serializer):
    source_language = serializers.CharField(
        max_length=10, default="eng", required=False
    )
    target_language = serializers.CharField(
        max_length=10, default="sme", required=False
    )
    text = serializers.CharField()


class TranscriptSerializer(serializers.Serializer):
    file = serializers.FileField()


class AudioRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioRequest
        fields = "__all__"
        read_only_fields = [
            "user",
            "transcribed_text",
            "translated_text",
            "instruction",
            "gpt_response",
            "instruction",
            "translated_response",
            "created_at",
            "response_audio"
        ]

    def validate_audio(self, value):
        # Check the MIME type of the uploaded file
        mime_type, _ = mimetypes.guess_type(value.name)
        if not mime_type or not mime_type.startswith("audio"):
            raise serializers.ValidationError(
                "The uploaded file is not a valid audio file."
            )
        return value
from pydub import AudioSegment

class UsersAllAudioRequestSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = AudioRequest
    #     fields = '__all__'
    audio_duration = serializers.SerializerMethodField()
    response_audio_duration = serializers.SerializerMethodField()

    class Meta:
        model = AudioRequest
        fields = ['user', 'page_number', 'audio', 'audio_duration', 'response_audio', 'response_audio_duration',
                  'instruction', 'transcribed_text', 'translated_text', 'gpt_response', 'translated_response',
                  'created_at']

    def get_audio_duration(self, obj):
        if obj.audio:
            audio_file_path = obj.audio.path
            audio = AudioSegment.from_file(audio_file_path)
            return len(audio) / 1000.0  # duration in seconds
        return None

    def get_response_audio_duration(self, obj):
        if obj.response_audio:
            response_audio_file_path = obj.response_audio.path
            response_audio = AudioSegment.from_file(response_audio_file_path)
            return len(response_audio) / 1000.0  # duration in seconds
        return None

class RequestCounterSerializer(serializers.ModelSerializer):
    # Define the fields to be used for the response
    user = serializers.ReadOnlyField(source='user.id')  # This will be read-only and automatically set
    page_number = serializers.IntegerField()  # This field will be required in the request
    request_count = serializers.ReadOnlyField()  # Read-only for response
    last_request_at = serializers.ReadOnlyField()  # Read-only for response

    class Meta:
        model = RequestCounter
        fields = ['user', 'page_number', 'request_count', 'last_request_at']
# class AudioRequestQuerySerializer(serializers.Serializer):
#     page_number = serializers.IntegerField()
#     user = serializers.EmailField()