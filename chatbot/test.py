from transformers import TFGPT2LMHeadModel, GPT2Tokenizer
import re

class GPT2Chatbot:
    def __init__(self):
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = TFGPT2LMHeadModel.from_pretrained('gpt2')
        self.tokenizer.pad_token = self.tokenizer.eos_token  # Set pad token to eos token

    def generate_response(self, query):
        # Encode the input query
        inputs = self.tokenizer(query, return_tensors='tf', padding=True, truncation=True)
        
        # Generate a response using the GPT-2 model
        outputs = self.model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],  # Provide attention mask
            max_length=150,                          # Increased max_length for longer responses
            temperature=0.7,                        # Adjust temperature for creativity
            top_k=50,                               # Adjust top_k to control output randomness
            top_p=0.9,                              # Use nucleus sampling (top_p) for better diversity
            eos_token_id=self.tokenizer.eos_token_id, # Use eos_token_id for stopping
            do_sample=True,                         # Ensure sampling is enabled
            no_repeat_ngram_size=2                  # Avoid repeating n-grams
        )
        
        # Decode the generated response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = self.clean_response(response)
        return response

    def clean_response(self, text):
        # Remove repetitive phrases
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text)  # Remove consecutive duplicate words
        sentences = re.split(r'(?<=[.!?]) +', text)  # Split text into sentences
        unique_sentences = list(dict.fromkeys(sentences))  # Remove duplicates while preserving order
        return ' '.join(unique_sentences).strip()

# Instantiate the chatbot and test it
if __name__ == "__main__":
    chatbot = GPT2Chatbot()
    test_query = "tell me something about pakistan"
    response = chatbot.generate_response(test_query)
    print(f"Response: {response}")
