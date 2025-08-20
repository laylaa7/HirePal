import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load CVs
with open("cvs.json", "r") as f:
    cvs = json.load(f)

# 2. Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # lightweight, fast

# 3. Create embeddings for CVs
cv_texts = [cv["text"] for cv in cvs]
cv_embeddings = model.encode(cv_texts)

# Convert to numpy float32 (FAISS requirement)
cv_embeddings = np.array(cv_embeddings).astype("float32")

# 4. Initialize FAISS index
dim = cv_embeddings.shape[1]
index = faiss.IndexFlatL2(dim)  # L2 distance
index.add(cv_embeddings)

# 5. Search function
def search(query, top_k=2):
    query_vec = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, top_k)
    results = []
    for idx in indices[0]:
        results.append(cvs[idx])
    return results

# 6. Try a query
if __name__ == "__main__":
    query = input("Enter your query: ")
    results = search(query, top_k=2)
    print("\nTop matches:")
    for r in results:
        print(f"- {r['name']}: {r['text']}")
