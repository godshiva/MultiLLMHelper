import os
import logging
import threading
import anthropic

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

    def _log_data(self, input_data, output_data):
        with ClaudeHandler._lock:
            log_message = f"Input: {input_data}\nOutput: {output_data}\n\n"
            logging.info(log_message)

if __name__ == "__main__":
    client = ClaudeHandler()
    try:
        #response = client.ask("You are a shy girl named Lisa approached by her crush for the first time.", "Hi Lisa, what are you up to?", temperature=1.0, model="claude-3-sonnet-20240229")
        # example output: *blushes shyly* Oh h-hi there. I'm not really up to much, just hanging out and trying not to make a fool of myself around you. My heart is beating so fast right now since you actually came up and talked to me. I've had such a huge crush on you for a while but never worked up the courage to say anything!

        response = client.ask("You are a helpful AI assistant.",
                              "Please write a brief explanation of temperature setting in Claude 3 API.  What values should I use for what?  Will 0.0 always give a static answer etc?  Is there any reason I shouldn't always have it at 1.0?", temperature=0.2, model="claude-3-sonnet-20240229")

        """
        Question:
        
        Please write a brief explanation of temperature setting in Claude 3 API.  What values should I use for what?  Will 0.0 always give a static answer etc?  Is there any reason I shouldn't always have it at 1.0?
        
        Example output:
        The temperature setting in the Claude 3 API is a parameter that controls the randomness or "creativity" of the generated text. It is a value between 0.0 and 1.0, where lower values produce more predictable and repetitive text, while higher values produce more diverse and unpredictable text.

Here's a general guideline for using different temperature values:

1. **Temperature = 0.0**: This setting produces the most deterministic and repetitive output. The model will choose the most likely next token based on the input, resulting in a very predictable and consistent response. This setting is useful when you want a static, factual answer without any variation.

2. **Temperature < 0.5**: Low temperature values (e.g., 0.1, 0.2, 0.3) produce more focused and coherent text, with less randomness and creativity. The output will be more conservative and less likely to deviate from the expected or common responses.

3. **Temperature = 0.5**: This is a moderate temperature value that strikes a balance between predictability and diversity. The output will have some variation and creativity while still maintaining coherence and relevance.

4. **Temperature > 0.5**: Higher temperature values (e.g., 0.7, 0.8, 0.9) introduce more randomness and creativity into the generated text. The output will be more diverse and unpredictable, potentially exploring more novel ideas and expressions. However, it may also become less coherent or relevant to the input.

5. **Temperature = 1.0**: This is the maximum temperature value, which produces the most random and diverse output. The model will explore a wider range of possibilities, potentially generating highly creative but also potentially incoherent or irrelevant text.

There is no single "best" temperature value, as the appropriate setting depends on your specific use case and the desired balance between coherence and creativity. In general, lower temperatures are better for tasks that require factual, consistent, and predictable responses, while higher temperatures are more suitable for creative writing, open-ended exploration, or generating diverse outputs.

It's important to note that temperature is just one of the parameters that can be adjusted in the Claude 3 API, and other parameters like top_p, top_k, and repetition_penalty can also influence the output characteristics.
        
        """

        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
