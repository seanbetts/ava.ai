# modules/actions.py

import chainlit as cl

from llama_index import TrafilaturaWebReader

from modules.chatbot import handle_file_upload
from .utils import extract_first_200_words, num_tokens_from_string

import io
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import pyperclip
import requests
import PyPDF2
from io import BytesIO

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
        cl.Image(name="Wordcloud", display="inline", size="large", content=image_bytes),
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
    if ".pdf" in action.value:
        response = requests.get(action.value)
        response.raise_for_status()

        # Convert the response content to a BytesIO object
        pdf_content = BytesIO(response.content)

        # Read the PDF with PyPDF2
        pdf_reader = PyPDF2.PdfReader(pdf_content)

        text = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text.append(page.extract_text())
        pdf_text = "\n".join(text)
        extracted_text = extract_first_200_words(pdf_text)

        elements = [
            # cl.Pdf(name="PDF", display="inline", content=uploaded_file.content),
            cl.Text(name="Here are the first 200 words from the document:", content=extracted_text, display="inline")
        ]

        actions = [
            cl.Action(name="Summarise", value=f"{pdf_text}", description="Summarise!"),
            cl.Action(name="Bulletpoint Summary", value=f"{pdf_text}", description="Bulletpoint Summary!"),
            cl.Action(name="Create Wordcloud", value=f"{pdf_text}", description="Create Wordcloud!"),
            cl.Action(name="Copy", value=f"{pdf_text}", description="Copy Text!"),
            cl.Action(name="Save To Knowledgebase", value=f"{pdf_text}", description="Save To Knowledgebase!"),
        ]

        tokens = num_tokens_from_string(pdf_text, "gpt-3.5-turbo")

        await cl.Message(
            content=f"`The PDF contains {format(len(pdf_text), ',')} characters which is {format(tokens, ',')} tokens.", elements=elements, actions=actions
        ).send()

    else:
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

    # Retrieve the chain from the user session
    llm_chain = cl.user_session.get("llm_chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True

    # Call the chain asynchronously
    res = await llm_chain.acall(f"Write me a summary of this text:\n{action.value}", callbacks=[cb])
    answer = res["text"]

    actions = [
        cl.Action(name="Copy", value="This is the summary text", description="Copy Text!"),
        cl.Action(name="Save To Knowledgebase", value=answer, description="Save To Knowledgebase!"),
    ]

    await cl.Message(content=f"**Here is your summary:**\n\n{answer}", actions=actions).send()

    # Optionally remove the action button from the chatbot user interface
    # await action.remove()

###--WRITE BULLETPOINT SUMMARY--###
@cl.action_callback("Bulletpoint Summary")
async def on_action(action):

    # Retrieve the chain from the user session
    llm_chain = cl.user_session.get("llm_chain")
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True

    # Call the chain asynchronously
    res = await llm_chain.acall(f"Write me a bulletpoint summary of this text:\n{action.value}", callbacks=[cb])
    answer = res["text"]

    actions = [
        cl.Action(name="Copy", value="This is the bulletpoint summary text", description="Copy Text!"),
        cl.Action(name="Save To Knowledgebase", value=answer, description="Save To Knowledgebase!"),
    ]

    await cl.Message(content=f"**Here is your bulletpoint summary:**\n\n{answer}", actions=actions).send()

    # Optionally remove the action button from the chatbot user interface
    # await action.remove()

###--SAVE TO KNOWLEDGEBASE--###
@cl.action_callback("Save To Knowledgebase")
async def on_action(action):

    ## Add LLM query etc. here ##

    await cl.Message("**Knowledge Saved!**").send()

    # Optionally remove the action button from the chatbot user interface
    # await action.remove()