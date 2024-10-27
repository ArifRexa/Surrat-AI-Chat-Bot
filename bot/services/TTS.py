import urllib.parse as urlparse
from .api import login, send_command
def tts(chatgpt_response, filename):


    token = login("tim@valio.no", "8JP9F3ljR4SXc48E")
    if not token:
        print("Login failed")
        return

    text = chatgpt_response
    voice = "Elle22k_CO"
    text_quoted = urlparse.quote(text)

    output = "stream"
    response = send_command(token, voice, text_quoted, output, type="mp3")
    if response.status_code != 200:
        print("Failed to generate speech:", response.text)
        return

    file_path = f"./static/audio/{filename}"
    with open(file_path, "wb") as file:
        file.write(response.content)

    return file_path

# import urllib.parse as urlparse
#
#
#
#
# class TTSGenerator:
#     def __init__(self):
#         self.email = "tim@valio.no"
#         self.password = "8JP9F3ljR4SXc48E"
#         self.token = None
#
#     def login(self):
#         from api import login
#
#         self.token = login(self.email, self.password)
#         if not self.token:
#             print("Login failed")
#         return self.token
#
#     def generate_speech(self, chatgpt_response, voice="Elle22k_CO", output="stream", file_type="mp3"):
#         if not self.token:
#             print("No valid token. Please login first.")
#             return None
#
#         from api import send_command
#
#         text_quoted = urlparse.quote(chatgpt_response)
#         response = send_command(self.token, voice, text_quoted, output, type=file_type)
#
#         if response.status_code != 200:
#             print("Failed to generate speech:", response.text)
#             return None
#
#         return response.content
#
#     def save_to_file(self, file_content, filename):
#         file_path = f"./static/audio/{filename}"
#         with open(file_path, "wb") as file:
#             file.write(file_content)
#         return file_path
#
#     def tts(self, chatgpt_response, filename):
#         if not self.login():
#             return
#
#         audio_content = self.generate_speech(chatgpt_response)
#         if audio_content:
#             return self.save_to_file(audio_content, filename)
#         return None
