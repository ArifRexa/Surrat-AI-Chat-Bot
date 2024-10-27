import logging
import time
from .TTS import tts
# from .TTS import TTSGenerator
from .transcribe import Transcriber
from .translate import Translator
from bot.services.chat_response import GPTResponseHandler, ChatBot
from bot.serializers import AudioRequestSerializer

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.chatbot = ChatBot()

    def process_audio(self, file_data, filename):
        try:
            if filename.lower().endswith((".mp3", ".wav")):
                # Audio processing
                transcribed_text = self.transcriber.transcribe_voice(file_data)
                print("Transcribe: ", transcribed_text)
                if transcribed_text == 'Transcription failed or "text" key is missing':
                    return {"error": 'Transcription failed or "text" key is missing'}
                logger.info(f"Transcribed text: {transcribed_text}")

                translation_result = self.translator.perform_translation(
                    transcribed_text, "en", "en"
                )
                print(translation_result)
                translated_text = translation_result.get(
                    "Translated Text", transcribed_text
                )
                logger.info(f"Translated text: {translated_text}")

                chat_response = self.chatbot.chat_with_openai(translated_text)
                logger.info(f"Chat response: {chat_response}")
                print(chat_response)

                translation_result = self.translator.perform_translation(
                    chat_response, "en", "sme"
                )
                print(translation_result)
                translated_chat_response = translation_result.get(
                    "Translated Text", chat_response
                )
                logger.info(f"Translated chat response: {translated_chat_response}")

                final_text = translated_chat_response
                print(translated_chat_response)

                return {
                    "transcribed_text": transcribed_text,
                    "translated_text": translated_text,
                    "chat_response": chat_response,
                    "translated_chat_response": translated_chat_response,
                }

            else:
                return {"error": "Unsupported file format"}

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {"error": str(e)}

# tts("olla bures", 'output.mp3')

class ProcessData:
    def __init__(self, user):
        self.user = user
        self.transcriber = Transcriber()
        self.translator = Translator()
        self.gpt_handler = GPTResponseHandler(self.user)
        # self.tts = TTSGenerator()

    def process_audio(self, data):
        try:
            # Convert audio to text using the transcriber
            transcribed_text = self.transcriber.transcribe_voice(data["audio_file"])
            if not transcribed_text:
                raise ValueError(
                    "Transcription failed: No text was extracted from the audio."
                )
            print(f"Transcribed text: {transcribed_text}")

        except Exception as e:
            return {"error": f"Error during transcription: {str(e)}"}

        try:
            # Translate text to English
            translated_text = self.translator.perform_translation(
                text=transcribed_text, src_lang="sme", tgt_lang="nor"
            )
            print(f"Translated text: {translated_text}")

        except Exception as e:
            return {"error": f"Error during translation: {str(e)}"}

        try:
            print("In a AI services")
            # print("Here is data image: ",data["instruction_image"])
            if data.get("instruction_image"):
                gpt_response = self.gpt_handler.get_gpt_response(
                    current_text=translated_text,
                    instruction=data["instruction"],
                    instruction_image=data["instruction_image"]
                )
                print(f"GPT Response: {gpt_response}")

            else:

                # Send the translated text with the instruction to GPT/LLM
                gpt_response = self.gpt_handler.get_gpt_response(
                    current_text=translated_text,
                    instruction=data["instruction"],
                )
                print(f"GPT Response: {gpt_response}")

        except Exception as e:
            return {"error": f"Error during GPT response generation: {str(e)}"}

        try:
            # Translate GPT response to SME
            translated_response = self.translator.perform_translation(
                text=gpt_response, src_lang="nor", tgt_lang="sme"
            )
            print(f"Translated GPT Response: {translated_response}")

        except Exception as e:
            return {"error": f"Error during response translation: {str(e)}"}

        # timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format timestamp for readability
        # filename = f"Generated_Audio_nor_to_sami_{timestamp}.mp3"

        # try:
        #     # tts = self.tts.tts(translated_text, filename)
        #     from .TTS import tts
        #     tts(translated_response, filename)
        #
        # except Exception as e:
        #     return {"error": f"Error during TTS generation: {str(e)}"}
        #
        # print(f"transcribed_text:  {transcribed_text} , \n"
        #       f"translated_text: {translated_text}, \n"
        #       f"gpt_response: {gpt_response}, "
        #       f"translated_response:  {translated_response}, filename: {filename}")

        return {
            "transcribed_text": transcribed_text,
            "translated_text": translated_text,
            "gpt_response": gpt_response.strip('\"'),
            "translated_response": translated_response.strip('\"'),
            # 'filename': filename
        }



class ExternalProcessData:
    def __init__(self, user):
        self.user = user
        self.transcriber = Transcriber()

    def process_audio(self, data):
        try:
            # Convert audio to text using the transcriber
            transcribed_text = self.transcriber.transcribe_voice(data["audio_file"])
            if not transcribed_text:
                raise ValueError(
                    "Transcription failed: No text was extracted from the audio."
                )

            # Return the transcribed text
            return {"transcribed_text": transcribed_text}

        except Exception as e:
            return {"error": f"Error during transcription: {str(e)}"}
