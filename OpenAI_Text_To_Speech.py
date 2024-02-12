from pathlib import Path
import openai
from pydub import AudioSegment
from shutil import copyfile

class OpenAI_Text_To_Speech:
    def __init__(self):
        api_key_file = "keys/openai_api_key.txt"  # Go here to set up https://platform.openai.com/docs/api-reference/introduction
        self.api_key = self._read_api_key(api_key_file)
        self.client = openai.OpenAI(api_key=self.api_key)

    def _read_api_key(self, file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()

    def _split_text(self, big_string, max_length=4096):
        paragraphs = big_string.split('\n')
        for paragraph in paragraphs:
            assert len(paragraph) <= max_length, f"Found a paragraph longer than {max_length} characters"

        bundled_paragraphs = []
        current_bundle = ""
        for paragraph in paragraphs:
            if len(current_bundle) + len(paragraph) + 1 <= max_length:
                current_bundle += paragraph + "\n"
            else:
                bundled_paragraphs.append(current_bundle)
                current_bundle = paragraph + "\n"
        bundled_paragraphs.append(current_bundle)
        return bundled_paragraphs

    def _generate_speech(self, text_bundles, base_file_path, voice):
        file_paths = []
        for i, text in enumerate(text_bundles):
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text
            )
            file_path = base_file_path.parent / f"{base_file_path.stem}_{i}{base_file_path.suffix}"
            with open(file_path, "wb") as file:
                file.write(response.content)
            file_paths.append(file_path)
        return file_paths

    def _concatenate_audio(self, files, output_path, target_bitrate="320k"):
        if len(files) == 1:
            copyfile(files[0], output_path)
        else:
            combined = AudioSegment.empty()
            for file_path in files:
                audio_segment = AudioSegment.from_mp3(file_path)
                combined += audio_segment
                combined += AudioSegment.silent(duration=200)  # Duration is in milliseconds
            combined.export(output_path, format="mp3", bitrate=target_bitrate)

    def generate_and_save_speech(self, text, file_path_str, voice="echo"):
        file_path = Path(file_path_str)
        if not file_path.suffix == '.mp3':
            raise ValueError("File name must end with .mp3")
        if not file_path.parent.exists():
            raise FileNotFoundError("File path does not exist")

        bundled_paragraphs = self._split_text(text)
        generated_files = self._generate_speech(bundled_paragraphs, file_path,voice=voice)
        self._concatenate_audio(generated_files, file_path)
        # Clean up intermediate files
        for f in generated_files:
            f.unlink()

if __name__ == "__main__":
    sample = OpenAI_Text_To_Speech()
    sample.generate_and_save_speech("This is some sample text", "./example_output.mp3")