# modules/file_handlers.py

import chainlit as cl

import io
import PyPDF2
from pptx import Presentation
from docx import Document
import pandas as pd

from .utils import extract_first_200_words, num_tokens_from_string, get_token_limit, is_over_token_limit, dataframe_to_json_metadata

###--HANDLE PLAIN TEXT FILES--###
async def handle_text_file(uploaded_file, model):
    text = uploaded_file.content.decode("utf-8")
    extracted_text = extract_first_200_words(text)

    elements = [
        cl.Text(name="Here are the first 200 words from the document:", content=extracted_text, display="inline")
    ]

    actions = [
        cl.Action(name="Summarise", value=f"{text}", description="Summarise!"),
        cl.Action(name="Bulletpoint Summary", value=f"{text}", description="Bulletpoint Summary!"),
        cl.Action(name="Create Wordcloud", value=f"{text}", description="Create Wordcloud!"),
        cl.Action(name="Copy", value=f"{text}", description="Copy Text!"),
        cl.Action(name="Save To Knowledgebase", value=f"{text}", description="Save To Knowledgebase!"),
    ]

    tokens = num_tokens_from_string(text, model)
    token_limit = get_token_limit(model)
    is_over = is_over_token_limit(tokens, token_limit)

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(text), ',')} characters which is c.{format(tokens, ',')} tokens.\nYou're currently using the {model} model which has a token limit of {format(token_limit, ',')}.\n{is_over[1]}", elements=elements, actions=actions
    ).send()

###--HANDLE DOCs--###
async def handle_doc_file(uploaded_file, model):
    doc_content = io.BytesIO(uploaded_file.content)
    doc = Document(doc_content)
    extracted_text = []
    for para in doc.paragraphs:
        extracted_text.append(para.text)
    doc_text = "\n".join(extracted_text)
    extracted_text = extract_first_200_words(doc_text)

    elements = [
        cl.Text(name="Here are the first 200 words from the document:", content=extracted_text, display="inline")
    ]

    actions = [
        cl.Action(name="Summarise", value=f"{doc_text}", description="Summarise!"),
        cl.Action(name="Bulletpoint Summary", value=f"{doc_text}", description="Bulletpoint Summary!"),
        cl.Action(name="Create Wordcloud", value=f"{doc_text}", description="Create Wordcloud!"),
        cl.Action(name="Copy", value=f"{doc_text}", description="Copy Text!"),
        cl.Action(name="Save To Knowledgebase", value=f"{doc_text}", description="Save To Knowledgebase!"),
    ]
    
    tokens = num_tokens_from_string(doc_text, model)
    token_limit = get_token_limit(model)
    is_over = is_over_token_limit(tokens, token_limit)

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(doc_text), ',')} characters which is c.{format(tokens, ',')} tokens.\nYou're currently using the {model} model which has a token limit of {format(token_limit, ',')}.\n{is_over[1]}", elements=elements, actions=actions
    ).send()

###--HANDLE PDFs--###
async def handle_pdf_file(uploaded_file, model):
    # Load the PDF using PyPDF2
    pdf_content = io.BytesIO(uploaded_file.content)
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
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    tokens = num_tokens_from_string(pdf_text, model)
    token_limit = get_token_limit(model)
    is_over = is_over_token_limit(tokens, token_limit)

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(pdf_text), ',')} characters which is c.{format(tokens, ',')} tokens.\nYou're currently using the {model} model which has a token limit of {format(token_limit, ',')}.\n{is_over[1]}", elements=elements, actions=actions
    ).send()

###--HANDLE PPTs--###
async def handle_ppt_file(uploaded_file, model):
    ppt_content = io.BytesIO(uploaded_file.content)
    presentation = Presentation(ppt_content)
    extracted_text = []
    for slide in presentation.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                extracted_text.append(shape.text)
    ppt_text = "\n".join(extracted_text)
    extracted_text = extract_first_200_words(ppt_text)

    elements = [
        cl.Text(name="Here are the first 200 words from the document:", content=extracted_text, display="inline")
    ]

    actions = [
        cl.Action(name="Summarise", value=f"{ppt_text}", description="Summarise!"),
        cl.Action(name="Bulletpoint Summary", value=f"{ppt_text}", description="Bulletpoint Summary!"),
        cl.Action(name="Create Wordcloud", value=f"{ppt_text}", description="Create Wordcloud!"),
        cl.Action(name="Copy", value=f"{ppt_text}", description="Copy Text!"),
        cl.Action(name="Save To Knowledgebase", value=f"{ppt_text}", description="Save To Knowledgebase!"),
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    tokens = num_tokens_from_string(ppt_text, model)
    token_limit = get_token_limit(model)
    is_over = is_over_token_limit(tokens, token_limit)

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(ppt_text), ',')} characters which is c.{format(tokens, ',')} tokens.\nYou're currently using the {model} model which has a token limit of {format(token_limit, ',')}.\n{is_over[1]}", elements=elements, actions=actions
    ).send()

###--HANDLE XLSXs--###
async def handle_xlsx_file(uploaded_file):
    data = io.BytesIO(uploaded_file.content)
    df = pd.read_excel(data)

    # Convert first 5 rows to markdown
    markdown_content = df.head().to_markdown()

    # Store the dataframe in the user session
    cl.user_session.set("df", df)

    elements = [
        cl.Text(name="Here are the top 5 rows of data:", content=markdown_content, display="inline")
    ]

    actions = [
        cl.Action(name="Get Insights", value="data", description="Get Insights!"),
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded. It has {format(df.shape[0], ',')} rows and {format(df.shape[1], ',')} columns.", elements=elements, actions=actions
    ).send()

###--HANDLE CSVs--###
async def handle_csv_file(uploaded_file):
    data = io.BytesIO(uploaded_file.content)
    df = pd.read_csv(data)

    # Convert first 5 rows to markdown
    markdown_content = df.head().to_markdown()

    # Store the dataframe in the user session
    cl.user_session.set("df", df)

    elements = [
        cl.Text(name="Here are the top 5 rows of data:", content=markdown_content, display="inline")
    ]

    actions = [
        cl.Action(name="Get Insights", value="data", description="Get Insights!"),
        cl.Action(name="Upload File", value="temp", description="Upload File!"),
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded. It has {format(df.shape[0], ',')} rows and {format(df.shape[1], ',')} columns.", elements=elements, actions=actions
    ).send()

###--HANDLE IMAGEs--###
async def handle_image_file(uploaded_file):
    image_data = uploaded_file.content

    # Sending an image with the file name
    elements = [
    cl.Image(name=uploaded_file.name, display="inline", content=image_data)
    ]

    await cl.Message(content="Here's your image:", elements=elements).send()