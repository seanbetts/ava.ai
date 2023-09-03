import openai
import streamlit as st

openai.api_key = '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'

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "Ava.ai", "content": "**👋 Hi!**\n\nI'm **Ava** and can help you with lots of different tasks.\nI can help you find answers, get content from documents or webpages, summarise content and much more.\n\nI have a **Chat Model** for when we're chatting and an **Action Model** that runs actions.\n An action runs when you click a button below a chat message.\nAn action button looks like the **Upload File** button below ↓\n\n**Just ask me a question or upload a file to get started!**"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🦲"):
        st.markdown(prompt)

    with st.chat_message("Ava.ai", avatar="https://github.com/seanbetts/ava.ai/blob/main/assets/avatar.png?raw=true"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

st.button('Click me')