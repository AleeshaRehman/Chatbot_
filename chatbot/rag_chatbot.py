"""
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

class RAGChatbot:
    def __init__(self):
        # Initialize the Mistral AI client
        self.client = MistralClient()
        self.model_name = "mistral-medium-latest" 

    def generate_response(self, query):
        # Prepare the input messages
        messages = [
            ChatMessage(role="user", content=query)
        ]
        
        # Generate a response using the Mistral AI model
        chat_response = self.client.chat(
            model=self.model_name,
            messages=messages
        )
        
        # Extract and return the response text
        return chat_response.choices[0].message.content

        
from transformers import TFGPT2LMHeadModel, GPT2Tokenizer

class GPT2Chatbot:
    def __init__(self):
        # Load the GPT-2 model and tokenizer using TensorFlow
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = TFGPT2LMHeadModel.from_pretrained('gpt2')

    def generate_response(self, query):
        # Encode the input query
        inputs = self.tokenizer(query, return_tensors='tf')
        
        # Generate a response using the GPT-2 model
        outputs = self.model.generate(inputs['input_ids'])
        
        # Decode the generated response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
"""
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

api_key = ""
model = "mistral-large-latest"

client = MistralClient(api_key=api_key)

chat_response = client.chat(
    model=model,
    messages=[ChatMessage(role="user", content="tell me something about pakistan ")]
)

print(chat_response.choices[0].message.content)
