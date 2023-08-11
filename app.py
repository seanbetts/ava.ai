from langchain import PromptTemplate, OpenAI, LLMChain
from langchain.chat_models import ChatOpenAI

import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider

template = """Question: {question}

Answer: Let's think step by step."""


@cl.on_message
async def main(message: str):
    # Retrieve the chain from the user session
    llm_chain = cl.user_session.get("llm_chain")  # type: LLMChain

    # Call the chain asynchronously
    res = await llm_chain.acall(message, callbacks=[cl.AsyncLangchainCallbackHandler()])

    # Do any post processing here

    # "res" is a Dict. For this chain, we get the response by reading the "text" key.
    # This varies from chain to chain, you should check which key to read.
    await cl.Message(content=res["text"]).send()

@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            # Select(
            #     id="Model",
            #     label="OpenAI - Model",
            #     values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
            #     initial_index=0,
            # ),
            #Switch(id="Streaming", label="OpenAI - Stream Tokens", initial=True),
            Slider(
                id="Temperature",
                label="OpenAI - Temperature",
                initial=1,
                min=0,
                max=2,
                step=0.1,
            ),
        ]
    ).send()


@cl.on_settings_update
async def setup_agent(settings):
    print("Setup agent with following settings: ", settings)

    # Instantiate the chain for that user session
    prompt = PromptTemplate(template=template, input_variables=["question"])
    llm_chain = LLMChain(prompt=prompt, llm=OpenAI(temperature=settings["Temperature"]), verbose=True)

    # Store the chain in the user session
    cl.user_session.set("llm_chain", llm_chain)
