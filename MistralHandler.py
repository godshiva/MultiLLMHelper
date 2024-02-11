import os
import threading
import time

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

class MistralHandler():
    # Static lock shared by all instances
    _lock = threading.Lock()

    def __init__(self, api_key_file="./keys/mistral_api_key.txt", model="mistral-medium"):
        self.api_key = self.read_api_key(api_key_file)  # to set up API key go here: https://mistral.ai/
        self.client = MistralClient(api_key=self.api_key)
        self.model = model

    def read_api_key(self, file_path):
        with open(os.path.join(file_path), 'r') as file:
            return file.read().strip()

    def ask(self, content):
        try:
            assert content and isinstance(content, str) and len(content) > 0
            content = content.upper()

            messages = [ChatMessage(role="user", content=content)]
            chat_response = self.client.chat(model=self.model, messages=messages).choices[0].message.content

            self._log_data(content, chat_response)
            return chat_response

        except Exception as e:
            error_message = str(e)
            self._log_data(content, error_message)
            if "over rate limit" in error_message.lower():
                print("Overlimit")
                time.sleep(60)
            return error_message

    def _log_data(self, input_data, output_data):
        with MistralHandler._lock:
            log_message = f"Input: {input_data}\nOutput: {output_data}\n\n"
            os.makedirs(os.path.dirname('./logs/mistral.log'), exist_ok=True)
            with open('./logs/mistral.log', 'a', encoding="UTF-8", errors="replace") as log_file:
                log_file.write(log_message)

if __name__ == "__main__":
    client = MistralHandler()
    print(client.ask("Say hello!"))