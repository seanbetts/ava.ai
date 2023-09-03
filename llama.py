import os
import openai
from llama_index import VectorStoreIndex, SimpleDirectoryReader

openai.api_key = os.environ.get("OPENAI_API_KEY") or exit("OPENAI_API_KEY not set!")

documents = SimpleDirectoryReader('data-test').load_data()
index = VectorStoreIndex.from_documents(documents)