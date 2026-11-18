from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services import process_and_store_document, answer_rag_query

app = FastAPI(title="FastAPI Gemini LangChain RAG", version="1.0")

class QueryRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        result = await process_and_store_document(file)
        return {"status": "success", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(payload: QueryRequest):
    try:
        answer = await answer_rag_query(payload.question)
        return {"question": payload.question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "running", "service": "FastAPI RAG API with Gemini & Postgres"}