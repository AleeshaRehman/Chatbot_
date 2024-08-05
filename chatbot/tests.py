# test_rag_chatbot.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# Define a simplified RAGChatbot class for testing
class RAGChatbot:
    def __init__(self):
        # Initialize the Mistral AI client
        self.client = MistralClient()
        self.model_name = "mistral-medium-latest"  # Use the correct model name

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

class RAGChatbotTestCase(TestCase):
    
    @patch.object(MistralClient, 'chat')
    def test_generate_response(self, mock_chat):
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Paris is the capital of France."))
        ]
        mock_chat.return_value = mock_response
        
        # Instantiate the chatbot
        chatbot = RAGChatbot()
        
        # Test the generate_response method
        query = "What is the capital of France?"
        response = chatbot.generate_response(query)
        
        # Check if the response matches the expected output
        self.assertEqual(response, "Paris is the capital of France.")
        
        # Verify that the MistralClient's chat method was called with the correct parameters
        mock_chat.assert_called_once_with(
            model="mistral-medium-latest",
            messages=[
                ChatMessage(role="user", content=query)
            ]
        )
