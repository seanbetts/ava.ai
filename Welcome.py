import streamlit as st

st.set_page_config(
    page_title="Welcome",
    page_icon="👋"
)

with st.container():
    '''
    # Welcome to Ava.ai
    ![Ava](https://github.com/seanbetts/ava.ai/blob/main/assets/avatar%20-%20sqircle.png?raw=true)
    ### **👋 Hi there!**
    I'm **Ava** and I can help you with every day tasks. Currently I can help you with the following:
    - I can search the internet for you 🔍
    - I can get the latest news on any topic for you 📰
    - I can get images from the internet for you 🖼️
    - I can get information from Wikipedia for you 📖
    - I can look up any movie, tv show or actor for you 🎬📺🎭
    - I can do complex maths problems ➗✖️➕➖
    - I can ingest lots of different documents, data, and images 📄📊🖼️
    - I can get content from webpages 🌐
    - I can produce summaries and wordclouds of your content 📝☁️
    - I can copy content to your clipboard 📋
    - I can save content to your own personal knowledgebase 📚

    🔐 Any data saved is completely yours and saved into a local database that no one else can access.

    If you have any issues or feature requests please visit the [GitHub Repository](https://github.com/seanbetts/ava.ai)
    '''

st.divider()
st.button('Let\'s Chat', use_container_width=True)