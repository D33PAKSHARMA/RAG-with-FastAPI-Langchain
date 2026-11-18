from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from app.config.config import env


def get_embeddings_model():
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=env.GOOGLE_API_KEY,
    )


async def get_vector_store():
    embeddings = get_embeddings_model()
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name="rag_documents",
        connection=env.DATABASE_URL,
        use_jsonb=True,
        async_mode=True,
    )
    return vector_store