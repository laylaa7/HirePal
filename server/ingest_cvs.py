# file: ingest_cvs.py
import io, re, uuid
from typing import List
from google.cloud import storage, aiplatform
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai.vectorstores import VectorSearchVectorStore
from langchain.schema import Document
from pypdf import PdfReader

from config_manager import ConfigManager

# Get the single instance of the configuration
config = ConfigManager()

PROJECT_ID = config.PROJECT_ID
REGION = config.REGION
BUCKET = "cv-rag-west-4"
DIMENSIONS = config.DIMENSIONS
GCS_PREFIX = ""   # where you uploaded CVs 
INDEX_ID = "3037589987731177472"
INDEX_DISPLAY_NAME = "cv-index-rag"
ENDPOINT_ID = "7123093721570082816"

# 1) Init clients
aiplatform.init(project=PROJECT_ID, location=REGION)
gcs = storage.Client(project=PROJECT_ID)
bucket = gcs.bucket(BUCKET)

# 2) Helper: read PDF bytes from GCS and extract text
def pdf_text_from_blob(blob) -> str:
    bio = io.BytesIO(blob.download_as_bytes())
    reader = PdfReader(bio)
    pages = [p.extract_text() or "" for p in reader.pages]
    return "\n".join(pages)

# 3) List CV files
blobs = list(gcs.list_blobs(BUCKET, prefix=GCS_PREFIX))
pdf_blobs = [b for b in blobs if b.name.lower().endswith(".pdf")]

# 4) Convert each PDF to LangChain Document with metadata
docs: List[Document] = []
for b in pdf_blobs:
    text = pdf_text_from_blob(b)
    # very light cleanup
    text = re.sub(r"\s+\n", "\n", text)
    docs.append(Document(
        page_content=text,
        metadata={
            "gcs_uri": f"gs://{BUCKET}/{b.name}",
            "filename": b.name.split("/")[-1]
        }
    ))

# 5) Chunk for retrieval
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# 6) Embeddings (Vertex AI)
emb = VertexAIEmbeddings(
    model_name="text-embedding-005",  # or "gemini-embedding-001"
    project=PROJECT_ID,
    location=REGION,
)

# 7) Connect to the existing Vector Search index/endpoint
index = aiplatform.MatchingEngineIndex(INDEX_ID)
endpoint = aiplatform.MatchingEngineIndexEndpoint(ENDPOINT_ID)

vector_store = VectorSearchVectorStore.from_components(
    embedding=emb,
    index_id=INDEX_ID,
    endpoint_id=ENDPOINT_ID,
    gcs_bucket_name=BUCKET,
    project_id=PROJECT_ID,
    region=REGION,
)

# 8) Upsert texts
texts = [c.page_content for c in chunks]
metas = [c.metadata for c in chunks]
ids = [str(uuid.uuid4()) for _ in chunks]

vector_store.add_texts(texts=texts, metadatas=metas, ids=ids)
print(f"Upserted {len(ids)} chunks.")
