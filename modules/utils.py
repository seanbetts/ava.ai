# modules/utils.py

def extract_first_200_words(text):
    words = text.split()  # Split the text by whitespace
    return ' '.join(words[:200])  # Take the first 200 words and join them back into a string