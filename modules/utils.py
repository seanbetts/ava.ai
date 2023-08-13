# modules/utils.py

import tiktoken
import pandas as pd

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

## Returns the token limit for a given LLM
def get_token_limit(model_name):
    token_limits = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
    }

    return token_limits.get(model_name.lower(), "Unknown model")

## Returns whether the text is too big for the current model
def is_over_token_limit(tokens, token_limit):
    if tokens > token_limit:
        over_by = tokens - token_limit
        return True, f"**The text is over by {format(over_by, ',')} tokens for the current model.**"
    else:
        return False, "**The text is within the token limit.**"

## Returns JSON data and metadata from a pandas dataframe
def dataframe_to_json_metadata(df):
    """
    Converts a pandas dataframe to a JSON format with metadata.
    
    Parameters:
    - df (pandas.DataFrame): The input dataframe.
    
    Returns:
    - dict: A dictionary with two keys - 'data' and 'metadata'.
            'data' contains the dataframe in JSON format.
            'metadata' contains relevant metadata like column names, data types, and row/column counts.
    """
    
    # Convert dataframe to JSON format
    data_json = df.to_dict(orient='records')
    
    # Extract metadata
    metadata = {
        'num_rows': len(df),
        'num_columns': len(df.columns),
        'column_names': list(df.columns),
        'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    
    return {
        'data': data_json,
        'metadata': metadata
    }