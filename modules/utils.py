# modules/utils.py

import tiktoken

## Extracts the first 200 words from a string
def extract_first_200_words(text):
    words = text.split()  # Split the text by whitespace
    return ' '.join(words[:200])  # Take the first 200 words and join them back into a string

## Counts the number of tokens in a string, rounded to the nearest 10
def num_tokens_from_string(string: str, model_name: str) -> int:
    """Returns the number of tokens in a text string rounded to the nearest 10."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    rounded_tokens = round(num_tokens / 10) * 10
    return rounded_tokens