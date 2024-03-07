import os
import logging
import threading
import anthropic
import base64
import mimetypes

# Configure logging
log_file_path = './logs/ClaudeHandler.log'
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ClaudeHandler:
    _lock = threading.Lock()

    def __init__(self):
        api_key_file = "keys/claude_key.txt"  # Go here to set up https://console.anthropic.com/
        self.client = anthropic.Anthropic(api_key=self.read_api_key(api_key_file))

    def read_api_key(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except Exception as e:
            logging.error(f"Error reading API key: {e}")
            raise

    def ask(self, system, content, max_tokens=4096, temperature=0.2, model="claude-3-opus-20240229"):
        """
        Claude 3 Opus	claude-3-opus-20240229
        Claude 3 Sonnet	claude-3-sonnet-20240229
        Claude 3 Haiku	Coming soon

        """

        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[
                    {"role": "user", "content": content}
                ]
            )
            try:
                self._log_data(content, str(message.content))

                assert len(message.content) == 1 and message.content[
                    0].type == "text", f"Unexpected data format returned. {message.content}"

                return message.content[0].text
            except Exception as e:
                logging.error(f"Error processing message content: {e}")
                raise

        except Exception as e:
            logging.error(f"Error in ask method: {e}")
            raise

    def ask_with_files(self, system, content, files, max_tokens=4096, temperature=0.2, model="claude-3-opus-20240229"):
        try:
            # Prepare the content list with the initial text message
            messages_content = [{"role": "user", "content": [{"type": "text", "text": content}]}]

            # Loop through each file in files, read and encode it to base64, and append to messages_content
            for file_path in files:
                try:
                    # Determine the file's MIME type
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type is None or not mime_type.startswith('image/'):
                        logging.error(f"Unsupported or unknown file type for file {file_path}")
                        continue  # Skip this file if the MIME type is not supported or unknown

                    with open(file_path, "rb") as image_file:
                        image_data = base64.b64encode(image_file.read()).decode("utf-8")
                        image_message = {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_data,
                            }
                        }
                        # Append image data to the content list
                        messages_content[0]["content"].append(image_message)
                except Exception as e:
                    logging.error(f"Error processing file {file_path}: {e}")
                    continue  # Skip this file and continue with the next

            # Create the message with files included
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=messages_content
            )

            try:
                self._log_data(content, str(message.content))

                assert len(message.content) == 1 and message.content[0].type == "text", "Unexpected data format returned."

                return message.content[0].text
            except Exception as e:
                logging.error(f"Error processing message content: {e}")
                raise

        except Exception as e:
            logging.error(f"Error in ask_with_files method: {e}")
            raise




    def _log_data(self, input_data, output_data):
        with ClaudeHandler._lock:
            log_message = f"Input: {input_data}\nOutput: {output_data}\n\n"
            logging.info(log_message)

if __name__ == "__main__":

    client = ClaudeHandler()
    response = client.ask("You are a helpful assistant.", "Say hi", model="claude-3-sonnet-20240229")
    print(response)
    """
    Hi there!
    """

    # response = client.ask_with_files("You are a helpful assistant..", "What animals are in the attached images?.",files=[r"dog.png", r"horse.png"],  temperature=0.1, model="claude-3-sonnet-20240229")
    """
    Image response
    The first image shows a bulldog, which is a breed of dog. The bulldog has a distinctive wrinkly face and is lying down on the floor.

    The second image depicts a horse. It is a reddish-brown or chestnut colored horse standing in what appears to be a grassy, outdoor area with some trees or foliage in the background.

    """
    #print(response)
