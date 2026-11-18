import os
import shutil
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.config.database import get_vector_store
from app.config.config import env

UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


async def process_and_store_document(file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    docs = []
    if file.filename.endswith(".pdf"):
        from langchain_community.document_loaders import PyMuPDFLoader
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
    elif file.filename.endswith(".docx"):
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
    else:
        os.remove(file_path)
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")

    os.remove(file_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunked_docs = text_splitter.split_documents(docs)

    vector_store = await get_vector_store()
    await vector_store.aadd_documents(chunked_docs)

    return {"filename": file.filename, "chunks_indexed": len(chunked_docs)}


async def answer_rag_query(question: str):
    vector_store = await get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    primary_llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        google_api_key=env.GOOGLE_API_KEY,
        temperature=0.3,
        max_retries=1,
        timeout=60,
    )

    fallback_llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=env.GOOGLE_API_KEY,
        temperature=0.3,
        max_retries=2,
        timeout=60,
    )

    llm = primary_llm.with_fallbacks([fallback_llm])

    prompt = ChatPromptTemplate.from_template("""
    Answer the user's question accurately using only the provided context below.
    If you do not know the answer based on the context, state that you don't know clearly.

    Context:
    {context}

    Question: {input}
    """)

    rag_chain = (
        {"context": retriever | _format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return await rag_chain.ainvoke(question)