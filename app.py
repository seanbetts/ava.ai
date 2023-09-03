import os
import openai
import asyncio

from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain import PromptTemplate, LLMChain
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper

import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider
from modules import actions
from modules.chatbot import handle_url_message
from modules.utils import get_token_limit, generate_actions
from modules.tools import NewsSearchTool, WikipediaSearchTool, YouTubeSearchTool, GoogleMapsSearchTool, GoogleImageSearchTool, GoogleSearchTool, SpotifySearchTool, TMDBSearchTool

openai.api_key = os.environ.get("OPENAI_API_KEY") or exit("OPENAI_API_KEY not set!")

template = """
Question: {question}
Answer: Let's think step by step.
"""

qna_template = """
{question}
"""

search = GoogleSearchTool()
news = NewsSearchTool()
wikipedia = WikipediaSearchTool()
youtube = YouTubeSearchTool()
images = GoogleImageSearchTool()
maps = GoogleMapsSearchTool()
music = SpotifySearchTool()
movie = TMDBSearchTool()
wolfram = WolframAlphaAPIWrapper(wolfram_alpha_appid = os.environ.get("WOLFRAM_ALPHA_APPID"))

tools = [
    Tool(
        name = "Maths",
        func=wolfram.run,
        description="Use this when you want need to do maths or make some calculations. Use this more than any other tool if the question is about maths or making calculations. The input to this should be numbers in a maths expression",
        return_direct=True
    ),
    # Tool(
    #     name = "Video Search",
    #     func=youtube.run,
    #     description="Use this when you want to search for YouTube videos or movie trailers. Use this more than Internet Search if the question is about videos or trailers. The input to this should be a single search term.",
    #     return_direct=True
    # ),
    # Tool(
    #     name = "Map & Location Search",
    #     func=maps.run,
    #     description="Use this when you want to search for a map or get a location. Use this more than any other tool if the question is about locations or maps. The input to this should be a single search term.",
    #     return_direct=True
    # ),
    Tool(
        name = "Image Search",
        func=images.run,
        description="Use this when you want to search for images. Use this more than any other tool if the question is about images. The input to this should be a single search term.",
        return_direct=True
    ),
    Tool(
        name = "Wikipedia Search",
        func=wikipedia.run,
        description="Use this when you want to search wikipedia about things you have no knowledge of. Use this more than Internet Search if the question is about Wikipedia. The input to this should be a single search term.",
        return_direct=True
    ),
    Tool(
        name = "Internet Search",
        func=search.run,
        description="Use this when you want to search the internet to answer questions about things you have no knowledge of. The input to this should be a single search term.",
        return_direct=True
    ),
    Tool(
        name = "Latest News Search",
        func=news.run,
        description="Use this when you want to get information about the latest news, top news headlines or current news stories. Use this more than Internet Search if the question is about News. The input should be a question in natural language that this API can answer.",
        return_direct=True
    ),
    # Tool(
    #     name = "Music Search",
    #     func= music.run,
    #     description="Use this when you want to search for music. Use this more than any other tool if the question is about music. The input to this should be a single search term.",
    #     return_direct=True
    # ),
    Tool(
        name = "Movie & TV Search",
        func= movie.run,
        description="Use this when you want to search for a movie, tv show or actor. Use this more than any other tool if the question is about movies, tv shows or actors. The input to this should be a single search term.",
        return_direct=True
    )
]

@cl.cache
def get_memory():
    return ConversationBufferMemory(memory_key="chat_history")

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
    qna_prompt = PromptTemplate(template=qna_template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=action_model, verbose=True)
    agent_chain = initialize_agent(tools, chat_model, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
    qna_chain = LLMChain(prompt=qna_prompt, llm=action_model, verbose=True)

    # Store the model & chain in the user session
    cl.user_session.set("chat_model", settings['Chat_Model'])
    cl.user_session.set("action_model", settings['Action_Model'])
    cl.user_session.set("llm_chain", llm_chain)
    cl.user_session.set("agent_chain", agent_chain)
    cl.user_session.set("qna_chain", qna_chain)

    await cl.Avatar(
        name="seanbetts@icloud.com",
        url="https://github.com/seanbetts/va.ai/blob/main/assets/seanbetts.png?raw=true",
    ).send()
    
    await cl.Avatar(
        name="ava.ai",
        url="https://github.com/seanbetts/ava.ai/blob/main/assets/avatar.png?raw=true",
    ).send()

    actions = [
        cl.Action(name="Upload File", value="temp", description="Upload any file you'd like help with"),
    ]

    await asyncio.sleep(2)
    await cl.Message(
        content=f"**👋 Hi!**\n\nI'm **Ava** and can help you with lots of different tasks.\nI can help you find answers, get content from documents or webpages, summarise content and much more.\n\nI have a **Chat Model** for when we're chatting and an **Action Model** that runs actions.\n An action runs when you click a button below a chat message.\nAn action button looks like the **Upload File** button below ↓\n\n**Just ask me a question or upload a file to get started!**\n\nYou are currently using the following settings:\n\n**Chat Model:** {settings['Chat_Model']} (max tokens of {format(get_token_limit(settings['Chat_Model']), ',')})\n**Action Model:** {settings['Action_Model']} (max tokens of {format(get_token_limit(settings['Action_Model']), ',')})\n**Temperature:** {settings['Temperature']}\n**Streaming:** {settings['Streaming']}\n\nYou can update these settings on the left of the chatbox below ↓\n___", actions=actions).send()

@cl.on_message
async def main(message):
    # Set Thinking message
    msg = cl.Message("**🤔 Thinking...**")
    await msg.send()

    # Empty clipboard
    cl.user_session.set("clipboard", None)

    # Retrieve the chain from the user session
    agent_chain = cl.user_session.get("agent_chain")
    qna_chain = cl.user_session.get("qna_chain")

    # Empty images in user session
    cl.user_session.set("image1", None)
    cl.user_session.set("image2", None)
    cl.user_session.set("image3", None)
    cl.user_session.set("image4", None)
    cl.user_session.set("image5", None)

    # Set up message streaming
    cb = cl.AsyncLangchainCallbackHandler(
        stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
    )
    cb.answer_reached = True

    content = cl.user_session.get("content")

    # Detect if a URL was included in the chat message from the user
    if content is not None:
        # Call the chain asynchronously
        res = qna_chain.run(f"Answer the following question based on the content below:\nQuestion: {message}\nContent: {content}", callbacks=[cb])

        # Empty content from user session
        # cl.user_session.set("content", None)

        action_keys = ["another_question", "end_questions", "copy", "save_to_knowledgebase","upload_file"]
        actions = generate_actions("data", action_keys)

        cl.user_session.set("clipboard", res)

        await msg.remove()
        await cl.Message(content=f"{res}\n___", actions=actions).send()
    
    elif "http" in message or "www" in message:
        await msg.remove()
        await handle_url_message(message)

    else: 
         # Call the chain asynchronously
        res = agent_chain.run(message, callbacks=[cb])

        if "Here are your images:" in res:
            image1 = cl.user_session.get("image1")
            image2 = cl.user_session.get("image2")
            image3 = cl.user_session.get("image3")
            image4 = cl.user_session.get("image4")
            image5 = cl.user_session.get("image5")

            elements = [
                cl.Image(url=image1, name="Image 1", display="inline"),
                cl.Image(url=image2, name="Image 2", display="inline"),
                cl.Image(url=image3, name="Image 3", display="inline"),
                cl.Image(url=image4, name="Image 4", display="inline"),
                cl.Image(url=image5, name="Image 5", display="inline"),
            ]

        else:
            elements = []

        action_keys = ["copy","save_to_knowledgebase","upload_file"]
        actions = generate_actions("data", action_keys)

        await msg.remove()
        await cl.Message(content=f"{res}\n___", elements=elements, actions=actions).send()

@cl.on_settings_update
async def setup_agent(settings):
    # Instantiate the chain for that user session
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    chat_model = ChatOpenAI(model=settings['Chat_Model'], temperature=settings["Temperature"], streaming=settings["Streaming"])
    action_model = ChatOpenAI(model=settings['Action_Model'], temperature=settings["Temperature"], streaming=settings["Streaming"])
    prompt = PromptTemplate(template=template, input_variables=["question"])
    qna_prompt = PromptTemplate(template=qna_template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=action_model, verbose=True)
    agent_chain = initialize_agent(tools, chat_model, agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
    qna_chain = LLMChain(prompt=qna_prompt, llm=action_model, verbose=True)

    # Store the model & chain in the user session
    cl.user_session.set("chat_model", settings['Chat_Model'])
    cl.user_session.set("action_model", settings['Action_Model'])
    cl.user_session.set("llm_chain", llm_chain)
    cl.user_session.set("agent_chain", agent_chain)
    cl.user_session.set("qna_chain", qna_chain)

    action_keys = ["upload_file"]
    actions = generate_actions("data", action_keys)

    await cl.Message(
        content=f"You are now using the following settings:\n**Chat Model:** {settings['Chat_Model']} (max tokens of {format(get_token_limit(settings['Chat_Model']), ',')})\n**Action Model:** {settings['Action_Model']} (max tokens of {format(get_token_limit(settings['Action_Model']), ',')})\n**Temperature:** {settings['Temperature']}\n**Streaming:** {settings['Streaming']}", actions=actions).send()