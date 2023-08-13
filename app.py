import os
import openai
import asyncio

from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain import PromptTemplate, LLMChain
from langchain.utilities import SerpAPIWrapper

import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider
from modules import actions
from modules.chatbot import handle_url_message
from modules.utils import get_token_limit

openai.api_key = os.environ.get("OPENAI_API_KEY") or exit("OPENAI_API_KEY not set!")

template = """Question: {question}

Answer: Let's think step by step."""

search = SerpAPIWrapper()
tools = [
    Tool(
        name = "Current Search",
        func=search.run,
        description="useful for when you need to answer questions about current events or the current state of the world"
    ),
]

@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="Chat_Model",
                label="Chat Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"],
                initial_index=0,
            ),
            Select(
                id="Action_Model",
                label="Action Model",
                values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"],
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

    # Instantiate the chain for that user session
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chat_model = ChatOpenAI(model=settings['Chat_Model'], temperature=settings["Temperature"], streaming=settings["Streaming"])
    action_model = ChatOpenAI(model=settings['Action_Model'], temperature=settings["Temperature"], streaming=settings["Streaming"])
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=action_model, verbose=True)
    agent_chain = initialize_agent(tools, chat_model, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)

    # Store the model & chain in the user session
    cl.user_session.set("chat_model", settings['Chat_Model'])
    cl.user_session.set("action_model", settings['Action_Model'])
    cl.user_session.set("llm_chain", llm_chain)
    cl.user_session.set("agent_chain", agent_chain)

    await cl.Avatar(
        name="seanbetts@icloud.com",
        url="https://github.com/seanbetts/va.ai/blob/main/assets/seanbetts.png?raw=true",
    ).send()
    
    await cl.Avatar(
        name="va.ai",
        url="https://github.com/seanbetts/ava.ai/blob/main/assets/avatar.png?raw=true",
    ).send()

    actions = [
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    await asyncio.sleep(2)
    await cl.Message(
        content=f"**👋 Hi!**\n\nI'm **Ava** and can help you with lots of different tasks.\nI can help you find answers, get content from documents or webpages, summarise content and much more.\n\nI have a **Chat Model** for when we're chatting and an **Action Model** that runs actions.\n An action runs when you click a button below a chat message.\nAn action button looks like the **Upload File** button below ↓\n\n**Just ask me a question or upload a file to get started!**\n\nYou are currently using the following settings:\n\n**Chat Model:** {settings['Chat_Model']} (max tokens of {format(get_token_limit(settings['Chat_Model']), ',')})\n**Action Model:** {settings['Action_Model']} (max tokens of {format(get_token_limit(settings['Action_Model']), ',')})\n**Temperature:** {settings['Temperature']}\n**Streaming:** {settings['Streaming']}\n\nYou can update these settings in the chatbox below ↓", actions=actions).send()

@cl.on_message
async def main(message):
    # Retrieve the chain from the user session
    agent_chain = cl.user_session.get("agent_chain")

    # Set up message streaming
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True

    # Detect if a URL was included in the chat message from the user
    if "http" in message or "www" in message:
        await handle_url_message(message)

    else: 
         # Call the chain asynchronously
        res = agent_chain.run(message, callbacks=[cb])

        actions = [
            cl.Action(name="Upload File", value="temp", description="Upload File!"),
        ]

        # Do any post processing here

        await cl.Message(content=res, actions=actions).send()

@cl.on_settings_update
async def setup_agent(settings):
    # Instantiate the chain for that user session
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chat_model = ChatOpenAI(model=settings['Chat_Model'], temperature=settings["Temperature"], streaming=settings["Streaming"])
    action_model = ChatOpenAI(model=settings['Action_Model'], temperature=settings["Temperature"], streaming=settings["Streaming"])
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=action_model, verbose=True)
    agent_chain = initialize_agent(tools, chat_model, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)

    # Store the model & chain in the user session
    cl.user_session.set("chat_model", settings['Chat_Model'])
    cl.user_session.set("action_model", settings['Action_Model'])
    cl.user_session.set("llm_chain", llm_chain)
    cl.user_session.set("agent_chain", agent_chain)

    actions = [
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    await cl.Message(
        content=f"You are now using the following settings:\n**Chat Model:** {settings['Chat_Model']} (max tokens of {format(get_token_limit(settings['Chat_Model']), ',')})\n**Action Model:** {settings['Action_Model']} (max tokens of {format(get_token_limit(settings['Action_Model']), ',')})\n**Temperature:** {settings['Temperature']}\n**Streaming:** {settings['Streaming']}", actions=actions).send()