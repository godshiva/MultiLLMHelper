import os
import threading
import time
import traceback

import google.generativeai as genai  # pip install install google-cloud-aiplatform

class GeminiHander:  # formerly "Bard", sad, I liked the old name
    _lock = threading.Lock()

    def read_api_key(self, file_path):
        with GeminiHander._lock:
            with open(file_path, 'r') as file:
                return file.read().strip()

    def __init__(self):
        genai.configure(api_key=self.read_api_key("keys/bard_api_key.txt"))  # go here to get an API key https://makersuite.google.com/app/apikey

    def ask(self, content):
        try:
            model = genai.GenerativeModel('gemini-pro')  # switch to gemini-ultra as soon as it's available
            response = model.generate_content(content)
            self._log_data(content, response.text)
            return response.text
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self._log_data(content, error_message, error=True)
            return error_message

    def list_models(self):
        try:
            models = genai.list_models()
            return models
        except Exception as e:
            return f"Failed to list models: {str(e)}"

    def _log_data(self, input_data, output_data, error=False):
        with GeminiHander._lock:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"Timestamp: {timestamp}\nInput: {input_data}\nOutput: {output_data}\n\n"
            if error:
                log_message += f"Error: {traceback.format_exc()}\n\n"
            os.makedirs(os.path.dirname('./logs/Bard.log'), exist_ok=True)
            with open('./logs/Bard.log', 'a', encoding="UTF-8", errors="replace") as log_file:
                log_file.write(log_message)


if __name__ == "__main__":
    client = GeminiHander()
    print("Listing available models...")
    print(list(client.list_models()))
    print("Sending test request...")
    print(client.ask("Say hello and identify yourself!"))
