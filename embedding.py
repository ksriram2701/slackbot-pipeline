from sentence_transformers import SentenceTransformer
import numpy as np
cluster_model = SentenceTransformer(r"intfloat/e5-large-v2")
def get_embeddings(keywords):
    return cluster_model.encode(keywords, normalize_embeddings=True)


