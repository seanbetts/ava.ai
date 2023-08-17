# modules/utils.py

import chainlit as cl
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

## Returns the actions required
def generate_actions(text, action_keys=[]):
    # Define a dictionary with all possible actions and their attributes
    action_templates = {
        "summarise": {"name": "Summarise", "description": "This will write a one paragraph summary for you"},
        "bulletpoint_summary": {"name": "Bulletpoints", "description": "This will write a bullepoint summary for you"},
        "create_wordcloud": {"name": "Wordcloud", "description": "This will create a wordcloud for you"},
        "get_themes": {"name": "Themes", "description": "This will summarise the themes in the document"},
        "get_quotes": {"name": "Quotes", "description": "This will extract any quotes from the document"},
        "get_insights": {"name": "Get Insights", "description": "This will get you insights on your data"},
        "copy": {"name": "Copy", "description": "This will copy the text to your clipboard"},
        "save_to_knowledgebase": {"name": "Save To Knowledgebase", "description": "Save this to your personal knowledgebase"},
        "upload_file": {"name": "Upload File", "description": "Upload any file you'd like help with"}
    }

    actions = []
    for key in action_keys:
        if key in action_templates:
            template = action_templates[key]
            actions.append(cl.Action(name=template["name"], value=f"{text}", description=template["description"]))

    return actions

## Sends summary including number of tokens
async def send_file_message(uploaded_file, text_content, extracted_text, model, actions):
    tokens = num_tokens_from_string(text_content, model)
    token_limit = get_token_limit(model)
    is_over = is_over_token_limit(tokens, token_limit)
    
    await cl.Message(
        content=f"`{uploaded_file}` uploaded.\nIt contains {format(len(text_content), ',')} characters which is c.{format(tokens, ',')} tokens.\nYou're currently using the {model} model which has a token limit of {format(token_limit, ',')}.\n{is_over[1]}", 
        elements=[cl.Text(name="Here are the first 200 words from the document:", content=extracted_text, display="inline")], 
        actions=generate_actions(text_content, actions)
    ).send()