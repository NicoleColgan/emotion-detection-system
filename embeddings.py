from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams # model classes for configuring vector search
from sentence_transformers import SentenceTransformer   # generating text embeddings
import uuid

COLLECTION_NAME = "feedback_emotions"

# Connect to Qdrant using the docker-compose service name (`qdrant`) on port 6333
qdrant = QdrantClient(host="qdrant", port=6333) 

# Load a small, fast embedding model for generating text embeddings
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def ensure_collection() -> None:
    """
    Ensures the Qdrant collection exists before storing or searching data.
    """
    collections = qdrant.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION_NAME not in names:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,          # all-MiniLM-L6-v2 embedding size
                distance=Distance.COSINE,
            ),
        )


def embed_text(text: str) -> List[float]:
    """Convert text into an embedding vector."""
    emb = model.encode(text)    # create embedding
    return emb.tolist() # convert numpy array to python list


def store_feedback(text: str, emotion_result: Dict[str, Any]) -> None:
    """
    Store the feedback text and its detected emotions in Qdrant.
    emotion_result is the dict returned by emotion_detector, including dominant_emotion.
    """
    
    ensure_collection()
    vector = embed_text(text)

    payload = {
        "text": text,
        "dominant_emotion": emotion_result.get("dominant_emotion"),
        "emotions": {
            k: v for k, v in emotion_result.items() if k != "dominant_emotion"
        },
    }

    # update/insert - if the id is already there, it will just update
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[    # a point is a single entry into the db - you can insert one or many at the same time
            {
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": payload, # extra data attatched to the vector - doesnt effect embedding/similarity search
            }
        ],
    )


def search_feedback(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Semantic search over stored feedback using Qdrant.
    Returns a list of payloads with text + emotions.
    """
    ensure_collection()
    query_vec = embed_text(query)

    try:
        # query quandrant with API
        result = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vec,    # find similar vectors to thid one
            limit=limit,    # number of results
            with_payload=True,  # return payload
            with_vectors=False, # omit actual vector
        )

        # extract payloads and scored cleanly
        similarities = []
        for point in result.points:
            similarities.append({
                "id": point.id,
                "score": point.score,   # similarity
                "payload": point.payload
            })

        return {"matches": similarities}
    except Exception as e:
        print(f"Qdrant search error: {e}")
        return {"matches": [], "error": str(e)}