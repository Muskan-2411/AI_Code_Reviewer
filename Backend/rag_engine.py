import os
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from groq import Groq

# =====================================
# BASE DIRECTORY (for Railway compatibility)
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================================
# GROQ CLIENT (lazy — validated at request time)
# =====================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("⚠️  WARNING: GROQ_API_KEY not set. API calls will fail.")
    client = None
else:
    client = Groq(api_key=GROQ_API_KEY)

# =====================================
# EMBEDDING MODEL
# =====================================

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model loaded")

# =====================================
# VECTOR STORE
# =====================================

VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")

print("Loading vector store...")

index_path = os.path.join(VECTOR_STORE_DIR, "faiss_index")
docs_path = os.path.join(VECTOR_STORE_DIR, "documents.pkl")

if not os.path.exists(index_path) or not os.path.exists(docs_path):
    print("⚠️  WARNING: Vector store not found. Run build_vector_store.py first.")
    index = None
    documents = []
else:
    index = faiss.read_index(index_path)
    with open(docs_path, "rb") as f:
        documents = pickle.load(f)
    print(f"✅ Vector store loaded — {len(documents)} documents")

# =====================================
# REVIEW FUNCTION
# =====================================

def review_code(code):
    """Review code using RAG + Groq LLM."""

    # Validate client is available
    if client is None:
        return "❌ Error: GROQ_API_KEY is not configured on the server."

    try:
        # ----------------------------------
        # RAG: Retrieve relevant context
        # ----------------------------------
        context = ""

        if index is not None and len(documents) > 0:
            query_embedding = model.encode(
                [code],
                convert_to_numpy=True
            )
            query_embedding = np.array(
                query_embedding,
                dtype=np.float32
            )

            # Retrieve top-k docs
            k = min(3, len(documents))
            distances, indices = index.search(query_embedding, k)

            retrieved_docs = []
            for idx in indices[0]:
                if 0 <= idx < len(documents):
                    retrieved_docs.append(documents[idx])

            context = "\n\n".join(retrieved_docs)

        # ----------------------------------
        # Build prompt
        # ----------------------------------
        prompt = f"""
You are a strict but fair Senior Software Engineer.

Evaluate the code based on:
- correctness
- readability
- security
- performance
- best practices

REFERENCE CONTEXT:
{context}

CODE:
{code}

IMPORTANT SCORING RULE:
- 9-10: production ready, clean code
- 7-8: good code, minor issues
- 5-6: average code, several improvements needed
- 3-4: poor structure or multiple bugs
- 1-2: broken, insecure, or unusable

Return ONLY:
language :
⭐ Score: X/10  
⚠️ Main Issue: (only most important issue)  
💡 Suggestion: (only best improvement)  
📝 Summary: (one line only)

Be fair. Do NOT always assume security issues.
"""

        # ----------------------------------
        # Call Groq API
        # ----------------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=300
        )

        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        return f"❌ Error during review: {str(e)}"