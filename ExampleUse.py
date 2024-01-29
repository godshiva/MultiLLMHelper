from BardHandler import BardHandler
from GPT4Handler import GPT4Handler
from MistralHandler import MistralHandler
from GPT35Handler import GPT35Handler

for service in [BardHandler, GPT4Handler, GPT35Handler, MistralHandler]:
    print("----")
    print(service.__name__)
    print(service().ask("Identify yourself and say hello!"))

"""
Sample output

----
BardHandler
Hello! I am a sophisticated language model, developed to assist with various writing tasks. You can think of me as a versatile writing companion, here to help you express yourself effectively. However, I am still under development and learning to navigate the nuances of human language. I'm excited to assist you with your writing needs, and I'm always eager to learn and improve. Let's collaborate and craft some amazing content together! 😊
----
GPT4Handler
Hello! I am an AI developed by OpenAI, designed to interact with users and provide information, answer questions, and engage in conversation. How can I assist you today?
----
GPT35Handler
Hello! I am OpenAI's ChatGPT, a language model trained to assist with various tasks and have conversations. How can I help you today?
----
MistralHandler
Hello! I'm an AI language model, a helpful assistant designed to provide information and answer questions to the best of my ability. I'm here to make your life easier and help you with any inquiries you might have. How can I assist you today?


"""