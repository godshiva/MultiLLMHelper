import os
import threading

from openai import OpenAI # pip install openai

class GPT35Handler:
    # Static lock shared by all instances
    _lock = threading.Lock()

    def __init__(self):
        api_key_file="./keys/openai_api_key.txt"  # Go here to set up https://platform.openai.com/docs/api-reference/introduction
        self.api_key = self.read_api_key(api_key_file)

    def read_api_key(self, file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()

    def ask(self, content):
        client = OpenAI(api_key=self.api_key)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            model="gpt-3.5-turbo",

        )
        response = chat_completion.choices[0].message.content

        self._log_data(content, response)

        return response


    def _log_data(self, input_data, output_data):
        with GPT35Handler._lock:
            log_message = f"Input: {input_data}\nOutput: {output_data}\n\n"
            os.makedirs(os.path.dirname('./logs/GPT35.log'), exist_ok=True)
            with open('./logs/GPT35.log', 'a', encoding="UTF-8", errors="replace") as log_file:
                log_file.write(log_message)

if __name__ == "__main__":
    client = GPT35Handler()
    print(client.ask("Say hello and identify yourself!"))