import hdbscan
import umap.umap_ as umap
import numpy as np
from sentence_transformers import SentenceTransformer

centroid_model = SentenceTransformer(r"models\all-MiniLM-L6-v2")


def reduce_dimensionality(embeddings):
    reducer = umap.UMAP(
        n_neighbors=15,
        n_components=50,
        metric='cosine',
        random_state=42
    )
    return reducer.fit_transform(embeddings)

def cluster_keywords(reduced_embeddings, keywords, min_cluster_size=3):
    """
    Cluster reduced embeddings using HDBSCAN and map clusters to keyword strings.
    """
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=2,
        metric='euclidean',
        cluster_selection_epsilon=0.05
    )

    labels = clusterer.fit_predict(reduced_embeddings)
    clusters = {}

    # Map cluster labels to actual keyword strings
    for keyword, label in zip(keywords, labels):
        clusters.setdefault(label, []).append(keyword)

    return clusters, labels

def get_top_keywords(cluster_keywords_list, model, top_n=3):
    cluster_top_keywords = {}
    for cid, idx_list in cluster_keywords_list.items():
        embeddings = centroid_model.encode([cluster_keywords_list[cid][i] for i in range(len(idx_list))], normalize_embeddings=True)
        centroid = np.mean(embeddings, axis=0)
        distances = np.linalg.norm(embeddings - centroid, axis=1)
        top_indices = distances.argsort()[:top_n]
        cluster_top_keywords[cid] = [cluster_keywords_list[cid][i] for i in top_indices]
    return cluster_top_keywords
