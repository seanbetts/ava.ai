# modules/utils.py

import tiktoken

def extract_first_200_words(text):
    words = text.split()  # Split the text by whitespace
    return ' '.join(words[:200])  # Take the first 200 words and join them back into a string

def num_tokens_from_string(string: str, model_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens