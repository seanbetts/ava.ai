# modules/chatbot.py

import chainlit as cl
from .file_handlers import handle_text_file, handle_doc_file, handle_pdf_file, handle_ppt_file, handle_xlsx_file, handle_csv_file

async def handle_file_upload():
    files = None
    while files is None:
        files = await cl.AskFileMessage(content="Please upload a document to begin!", accept=["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.presentationml.presentation", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text/csv"]).send()
    uploaded_file = files[0]

    # Handling a plain text file
    if uploaded_file.type == "text/plain":
        await handle_text_file(uploaded_file)

    # Handling a docx file
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        await handle_doc_file(uploaded_file)

    # Handling a PDF file
    elif uploaded_file.type == "application/pdf":
        await handle_pdf_file(uploaded_file)

    # Handling a ppt file
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        await handle_ppt_file(uploaded_file)

    # Handling an Excel file
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        await handle_xlsx_file(uploaded_file)

    # Handling a CSV file
    elif uploaded_file.type == "text/csv":
       await  handle_csv_file(uploaded_file)

    else:
        await cl.Message(
            content=f"Unsupported file type uploaded."
        ).send()

async def handle_url_message(message):
    # Let the user know that your detected a url
    # Sending an action button within a chatbot message
    actions = [
        cl.Action(name="Get Website Content", value=f"{message}", description="Get Content!")
    ]

    await cl.Message(content=f"You gave me a URL to search : {message}", actions=actions).send()

async def handle_image_message():
    files = None
    while files == None:
        files = await cl.AskFileMessage(content="Please upload your image", accept=["image/jpeg", "image/gif", "image/png", "image/webp"]).send()

    # Decode the file
    image_file = files[0]
    image_data = image_file.content

    # Sending an image with the file name
    elements = [
    cl.Image(name=image_file.name, display="inline", content=image_data)
    ]

    await cl.Message(content="Here's your image:", elements=elements).send()