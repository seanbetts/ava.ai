# modules/file_handlers.py

import chainlit as cl

import io
import PyPDF2
from pptx import Presentation
from docx import Document
import pandas as pd

from .utils import extract_first_200_words

###--HANDLE PLAIN TEXT FILES--###
async def handle_text_file(uploaded_file):
    text = uploaded_file.content.decode("utf-8")
    extracted_text = extract_first_200_words(text)

    elements = [
        cl.Text(name="Here are the first 200 words from the document:", content=extracted_text, display="inline")
    ]

    actions = [
        cl.Action(name="Copy", value=f"{text}", description="Copy Text!"),
        cl.Action(name="Create Wordcloud", value=f"{text}", description="Create Wordcloud!")
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(text), ',')} characters...", elements=elements, actions=actions
    ).send()

###--HANDLE DOCs--###
async def handle_doc_file(uploaded_file):
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
        cl.Action(name="Copy", value=f"{doc_text}", description="Copy Text!"),
        cl.Action(name="Create Wordcloud", value=f"{doc_text}", description="Create Wordcloud!")
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(doc_text), ',')} characters from the DOCX...", elements=elements, actions=actions
    ).send()

###--HANDLE PDFs--###
async def handle_pdf_file(uploaded_file):
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
        cl.Text(name="Here are the first 200 words from the document:", content=extracted_text, display="inline")
    ]

    actions = [
        cl.Action(name="Copy", value=f"{pdf_text}", description="Copy Text!"),
        cl.Action(name="Create Wordcloud", value=f"{pdf_text}", description="Create Wordcloud!")
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(pdf_text), ',')} characters from the PDF...", elements=elements, actions=actions
    ).send()

###--HANDLE PPTs--###
async def handle_ppt_file(uploaded_file):
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
        cl.Action(name="Copy", value=f"{ppt_text}", description="Copy Text!"),
        cl.Action(name="Create Wordcloud", value=f"{ppt_text}", description="Create Wordcloud!")
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded, it contains {format(len(ppt_text), ',')} characters from the PPTX...", elements=elements, actions=actions
    ).send()

###--HANDLE XLSXs--###
async def handle_xlsx_file(uploaded_file):
    data = io.BytesIO(uploaded_file.content)
    df = pd.read_excel(data)

    # Convert first 5 rows to markdown
    markdown_content = df.head().to_markdown()

    elements = [
        cl.Text(name="Here are the top 5 rows of data:", content=markdown_content, display="inline")
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded. It has {df.shape[0]} rows and {df.shape[1]} columns.", elements=elements
    ).send()

###--HANDLE CSVs--###
async def handle_csv_file(uploaded_file):
    data = io.BytesIO(uploaded_file.content)
    df = pd.read_csv(data)

    # Convert first 5 rows to markdown
    markdown_content = df.head().to_markdown()

    elements = [
        cl.Text(name="Here are the top 5 rows of data:", content=markdown_content, display="inline")
    ]

    await cl.Message(
        content=f"`{uploaded_file.name}` uploaded. It has {df.shape[0]} rows and {df.shape[1]} columns.", elements=elements
    ).send()