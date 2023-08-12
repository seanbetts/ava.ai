import os
import openai
import asyncio

from llama_index.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.callbacks.base import CallbackManager
from llama_index import (
    LLMPredictor,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from langchain.chat_models import ChatOpenAI

import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider
from modules import actions
from modules.chatbot import handle_url_message

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
    settings = await cl.ChatSettings(
        [
            Select(
                id="Model",
                label="OpenAI - Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
                initial_index=0,
            ),
            Slider(
                id="Temperature",
                label="OpenAI - Temperature",
                initial=1.0,
                min=0,
                max=2,
                step=0.1,
            ),
            Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
        ]
    ).send()

    llm_predictor = LLMPredictor(
        llm=ChatOpenAI(
            temperature=settings["Temperature"],
            model_name=settings["Model"],
            streaming=settings["Streaming"],
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
        url="https://github.com/seanbetts/va.ai/blob/main/assets/seanbetts.png?raw=true",
    ).send()
    await cl.Avatar(
        name="va.ai",
        url="https://github.com/seanbetts/va.ai/blob/f100e27c5a31dfacdb7296b7afcad8ea3a33ebee/assets/chatAvatar.png?raw=true",
    ).send()

    actions = [
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    print(settings["Temperature"])

    await asyncio.sleep(2)
    await cl.Message(
        content=f"**Hi!**\n\nYou are currently using the following settings:\n**Model:** {settings['Model']}\n**Temperature:** {settings['Temperature']}\n**Streaming:** {settings['Streaming']}\n\nYou can update this in the settings below ↓", actions=actions).send()

@cl.on_message
async def main(message):
    query_engine = cl.user_session.get("query_engine")  # type: RetrieverQueryEngine

    if "http" in message or "www" in message:
        await handle_url_message(message)

    else: 
        response = await cl.make_async(query_engine.query)(message)

        response_message = cl.Message(content="")

        for token in response.response_gen:
            await response_message.stream_token(token=token)

        if response.response_txt:
            response_message.content = response.response_txt

        await response_message.send()

@cl.on_settings_update
async def setup_agent(settings):
    actions = [
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    await cl.Message(
        content=f"You are now using the following settings:\n**Model:** {settings['Model']}\n**Temperature:** {settings['Temperature']}\n**Streaming:** {settings['Streaming']}", actions=actions).send()

    # Instantiate the chain for that user session
    # prompt = PromptTemplate(template=template, input_variables=["question"])
    # llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=settings["Temperature"]), verbose=True)

    # Store the chain in the user session
    # cl.user_session.set("llm_chain", llm_chain)