import os
import openai

from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.callbacks.base import CallbackManager
from llama_index import (
    LLMPredictor,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
    TrafilaturaWebReader,
)
from langchain.chat_models import ChatOpenAI

import chainlit as cl


openai.api_key = os.environ.get("OPENAI_API_KEY")

try:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    # load index
    index = load_index_from_storage(storage_context)
except:
    from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader

    documents = SimpleDirectoryReader("./data").load_data()
    index = GPTVectorStoreIndex.from_documents(documents)
    index.storage_context.persist()


@cl.on_chat_start
async def factory():
    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo",
            streaming=True,
        ),
    )
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor,
        chunk_size=512,
        callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]),
    )

    query_engine = index.as_query_engine(
        service_context=service_context,
        streaming=True,
    )

    cl.user_session.set("query_engine", query_engine)
    await cl.Avatar(
        name="seanbetts@icloud.com",
        url="https://media.discordapp.net/attachments/1073252913226465380/1139636833068777482/kr4nos_voice_icon_neon_colors_clean_pixel_art_ed96e4a6-b05e-4656-90ca-e4ac9f154b9c.png?width=1372&height=1372",
    ).send()
    await cl.Avatar(
        name="va.ai",
        url="https://media.discordapp.net/attachments/1073252913226465380/1139636833068777482/kr4nos_voice_icon_neon_colors_clean_pixel_art_ed96e4a6-b05e-4656-90ca-e4ac9f154b9c.png?width=1372&height=1372",
    ).send()


@cl.on_message
async def main(message):
    query_engine = cl.user_session.get("query_engine")  # type: RetrieverQueryEngine
    if "file" in message:
        files = None
        while files == None:
            files = await cl.AskFileMessage(content="Please upload a text file to begin!", accept=["text/plain"]).send()

        # Decode the file
        text_file = files[0]
        text = text_file.content.decode("utf-8")

        # Let the user know that the system is ready
        await cl.Message(
            content=f"`{text_file.name}` uploaded, it contains {len(text)} characters..."
        ).send()

    elif "http" in message or "www" in message:
        # Let the user know that your detected a url
        # Sending an action button within a chatbot message
        actions = [
            cl.Action(name="Get Content", value=f"{message}", description="Get Content!")
        ]

        await cl.Message(content=f"You gave me a URL to search : {message}", actions=actions).send()

    elif "image" in message:
        files = None
        while files == None:
            files = await cl.AskFileMessage(content="Please upload your image", accept=["image/jpeg", "image/gif", "image/png", "image/webp"]).send()

        # Decode the file
        image_file = files[0]
        image_data = image_file.content

        # Sending an image with the local file path
        elements = [
        cl.Image(name=image_file.name, display="inline", content=image_data)
        ]

        await cl.Message(content="Here's your image:", elements=elements).send()

    else: 
        response = await cl.make_async(query_engine.query)(message)

        response_message = cl.Message(content="")

        for token in response.response_gen:
            await response_message.stream_token(token=token)

        if response.response_txt:
            response_message.content = response.response_txt

        await response_message.send()

@cl.action_callback("Get Content")
async def on_action(action):
    documents = TrafilaturaWebReader().load_data([action.value])

    elements = [
        cl.Text(name="Text from webpage:", content=f"{documents[0].text}", display="inline")
    ]

    await cl.Message(content=f"Retrieved text from {action.value}", elements=elements).send()

    # Optionally remove the action button from the chatbot user interface
    await action.remove()