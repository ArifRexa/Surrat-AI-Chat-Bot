import base64
import os
import requests


def encode_image(image_file):
    """
    Encodes an image file to a Base64 string.

    Parameters:
    - image_file: A file object representing the image.

    Returns:
    - A Base64 encoded string of the image content.
    """
    return base64.b64encode(image_file.read()).decode('utf-8')


def send_image_to_gpt(base64_image, text):
    """
    Sends a text and an image encoded in Base64 format to the GPT model via the OpenAI API.

    Parameters:
    - base64_image: A Base64 encoded string representing the image.
    - text: The text content to send alongside the image.

    Returns:
    - A JSON response from the OpenAI API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant in Norwegian Bokmål. You will always respond in Norwegian Bokmål, not in any other language. Please assist the user with their queries and images if there are any."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": f"instruction: {text}"
                    },
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()
