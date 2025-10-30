# rag_engine.py
import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Chroma configuration
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "ursaviour-data"
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

# Create Chroma client and collection
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

def get_embedding(text: str):
    """Generate embeddings using OpenAI"""
    emb = client.embeddings.create(model=EMBED_MODEL, input=text)
    return emb.data[0].embedding

def rag_query(question: str):
    """Perform retrieval-augmented generation"""
    q_emb = get_embedding(question)

    # Retrieve most relevant docs
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    top_docs = results['documents'][0]
    context = "\n".join(top_docs)

    prompt = f"""You are an assistant with access to the company's AWS data.

Context:
{context}

Question: {question}
Answer:"""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


from system_prompt_manager import get_system_prompt

def rag_query(question: str, tone: str = "default"):
    """Perform retrieval-augmented generation with tone control"""
    q_emb = get_embedding(question)
    results = collection.query(query_embeddings=[q_emb], n_results=3)
    top_docs = results['documents'][0]
    context = "\n".join(top_docs)

    system_prompt = get_system_prompt(tone)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
    ]

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages
    )
    return response.choices[0].message.content.strip()
