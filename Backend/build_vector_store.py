import os
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

# Base directory — ensures paths work on Railway
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Model loaded successfully")

knowledge_folder = os.path.join(BASE_DIR, "knowledge_base")

if not os.path.exists(knowledge_folder):
    raise Exception(
        f"{knowledge_folder} folder not found"
    )

documents = []

for filename in os.listdir(knowledge_folder):

    if filename.endswith(".txt"):

        filepath = os.path.join(
            knowledge_folder,
            filename
        )

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read().strip()

            if content:
                documents.append(content)

print(f"Documents loaded: {len(documents)}")

if len(documents) == 0:

    raise Exception(
        "No documents found in knowledge_base folder"
    )

print("Creating embeddings...")

embeddings = model.encode(
    documents,
    convert_to_numpy=True
)

embeddings = np.array(
    embeddings,
    dtype=np.float32
)

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(
    dimension
)

index.add(
    embeddings
)

vector_store_dir = os.path.join(BASE_DIR, "vector_store")

os.makedirs(
    vector_store_dir,
    exist_ok=True
)

faiss.write_index(
    index,
    os.path.join(vector_store_dir, "faiss_index")
)

with open(
    os.path.join(vector_store_dir, "documents.pkl"),
    "wb"
) as f:

    pickle.dump(
        documents,
        f
    )

print("\nVector Store Created Successfully")
print("Saved:")
print(f"  {vector_store_dir}/faiss_index")
print(f"  {vector_store_dir}/documents.pkl")