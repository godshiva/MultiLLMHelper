import requests
from openai import OpenAI


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
