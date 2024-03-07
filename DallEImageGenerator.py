import requests
from openai import OpenAI
import base64
import requests


class DallEImageGenerator():
    def __init__(self):
        api_key_file = "keys/openai_api_key.txt"  # Go here to set up https://platform.openai.com/docs/api-reference/introduction
        self.api_key = self._read_api_key(api_key_file)

    def _read_api_key(self, file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()


    def generate_image(self, description, save_path, resolution="1024x1024", model="dall-e-3", quality="standard"):
        if self.api_key is None:
            raise ValueError("API Key is not set.")

        # Assuming OpenAI's client initialization here
        client = OpenAI(api_key=self.api_key)

        response = client.images.generate(
            model=model,
            prompt=description,
            size=resolution,
            quality=quality,
            n=1,
        )

        if not response.data:
            raise Exception("Failed to fetch image from OpenAI.")

        image_url = response.data[0].url
        self.download_image(image_url, save_path)

    # todo: enable this when they make it available
    # def generate_image_from_image(self, description, save_path, input_image, resolution="1024x1024"):
    #     if self.api_key is None:
    #         raise ValueError("API Key is not set.")
    #     assert input_image is not None and isinstance(input_image, str) and ".png" in input_image, "Input image"
    #
    #     def encode_image(image_path):
    #         with open(image_path, "rb") as image_file:
    #             return base64.b64encode(image_file.read()).decode('utf-8')
    #
    #     image_path = input_image
    #
    #     base64_image = encode_image(image_path)
    #
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {self.api_key}"
    #     }
    #
    #     payload = {
    #         "model": "gpt-4-1106-vision-preview",
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": [
    #                     {
    #                         "type": "text",
    #                         "text": description
    #                     },
    #                     {
    #                         "type": "image_url",
    #                         "image_url": {
    #                             "url": f"data:image/png;base64,{base64_image}"
    #                         }
    #                     }
    #                 ]
    #             }
    #         ],
    #         "max_tokens": 2048
    #     }
    #
    #     response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    #
    #     print(response.json())


    def download_image(self, image_url, save_path):
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"Image downloaded successfully: {save_path}")
        else:
            raise Exception("Failed to download the image")


# Sample usage
if __name__ == "__main__":
    # Create an instance of the ImageGenerator class
    generator = DallEImageGenerator()
    generator.generate_image("A scenic view of the mountains at sunset", "sample.png")
