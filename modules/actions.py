# modules/actions.py

import chainlit as cl

from llama_index import TrafilaturaWebReader

from modules.chatbot import handle_file_upload

import io
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pyperclip

###--CREATE WORDCLOUD--###
@cl.action_callback("Create Wordcloud")
async def on_action(action):
    # Generate the wordcloud
    wordcloud = WordCloud(colormap='cool', background_color="rgba(0, 0, 0, 0)", mode="RGBA", stopwords=STOPWORDS, width=1980, height=1080, scale=1).generate(action.value)

    # Plot and save the word cloud
    fig = plt.figure(figsize=(19.80, 10.80))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout()

    # Saving the figure to a bytes buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png")

    # Convert the buffered image to bytes for sending
    image_bytes = buf.getvalue()

    # Sending an image with the file name
    elements = [
        cl.Image(name="Wordcloud", display="inline", content=image_bytes),
        cl.File(name="Wordcloud.png", content=image_bytes, display="inline")
    ]

    await cl.Message(content="Here's your wordcloud:", elements=elements).send()

    # Clear the current wordcloud figure
    plt.clf()

    # Remove the action button from the chatbot user interface
    # await action.remove()

###--GET WEBSITE CONTENT--###
@cl.action_callback("Get Website Content")
async def on_action(action):
    documents = TrafilaturaWebReader().load_data([action.value])

    elements = [
        cl.Text(name="Here is the text from the webpage:", content=f"{documents[0].text}", display="inline")
    ]

    actions = [
        cl.Action(name="Summarise", value=f"{documents[0].text}", description="Summarise!"),
        cl.Action(name="Bulletpoint Summary", value=f"{documents[0].text}", description="Bulletpoint Summary!"),
        cl.Action(name="Create Wordcloud", value=f"{documents[0].text}", description="Create Wordcloud!"),
        cl.Action(name="Copy", value=f"{documents[0].text}", description="Copy Text!"),
        cl.Action(name="Save To Knowledgebase", value=f"{documents[0].text}", description="Save To Knowledgebase!"),
    ]

    await cl.Message(content=f"Retrieved text from {action.value}", elements=elements, actions=actions).send()

    # Optionally remove the action button from the chatbot user interface
    await action.remove()

###--COPY--###
@cl.action_callback("Copy")
async def on_action(action):
    pyperclip.copy(action.value)

    await cl.Message(content=f"Text copied to clipboard").send()

    # Optionally remove the action button from the chatbot user interface
    await action.remove()

###--UPLOAD FILE--###
@cl.action_callback("Upload File")
async def on_action(action):
    await handle_file_upload("gpt-4")

    # Optionally remove the action button from the chatbot user interface
    await action.remove()

###--WRITE SUMMARY--###
@cl.action_callback("Summarise")
async def on_action(action):

    ## Add LLM query etc. here ##

    elements = [
        cl.Text(name="Here is your summary:", content="This is the summary text", display="inline")
    ]

    actions = [
        cl.Action(name="Copy", value="This is the summary text", description="Copy Text!"),
    ]

    await cl.Message(content=f"Retrieved text from {action.value}", elements=elements, actions=actions).send()

    # Optionally remove the action button from the chatbot user interface
    # await action.remove()

###--WRITE BULLETPOINT SUMMARY--###
@cl.action_callback("Bulletpoint Summary")
async def on_action(action):

    ## Add LLM query etc. here ##

    elements = [
        cl.Text(name="Here is your bulletpoint summary:", content="This is the bulletpoint summary text", display="inline")
    ]

    actions = [
        cl.Action(name="Copy", value="This is the bulletpoint summary text", description="Copy Text!"),
    ]

    await cl.Message(content=f"Retrieved text from {action.value}", elements=elements, actions=actions).send()

    # Optionally remove the action button from the chatbot user interface
    # await action.remove()

###--SAVE TO KNOWLEDGEBASE--###
@cl.action_callback("Save To Knowledgebase")
async def on_action(action):

    ## Add LLM query etc. here ##

    await cl.Message("Knowledge Saved!").send()

    # Optionally remove the action button from the chatbot user interface
    # await action.remove()