import os
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from groq import Groq

# =====================================
# GROQ API
# =====================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("Please set the GROQ_API_KEY environment variable")

client = Groq(
    api_key=GROQ_API_KEY
)

# =====================================
# EMBEDDING MODEL
# =====================================

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded")
# =====================================
# VECTOR STORE
# =====================================

print("Loading vector store...")

index = faiss.read_index("vector_store/faiss_index")

with open("vector_store/documents.pkl", "rb") as f:
    documents = pickle.load(f)

print("Vector store loaded")
print(f"Documents Loaded: {len(documents)}")

# =====================================
# REVIEW FUNCTION
# =====================================
def review_code(code):

    try:

        # Generate embedding
        query_embedding = model.encode(
            [code],
            convert_to_numpy=True
        )

        query_embedding = np.array(
            query_embedding,
            dtype=np.float32
        )

        # Retrieve top-k docs
        distances, indices = index.search(query_embedding, 3)

        retrieved_docs = []

        for idx in indices[0]:
            if 0 <= idx < len(documents):
                retrieved_docs.append(documents[idx])

        context = "\n\n".join(retrieved_docs)

    # =====================================
    # PROMPT INSIDE FUNCTION (FIXED)
    # =====================================

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

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=120
        )

        result = response.choices[0].message.content.strip()

        return result

    except Exception as e:
        return f"Error: {str(e)}"