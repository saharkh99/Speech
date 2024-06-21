# Fusion retrieval or hybrid search
# reranking
# Search Module — in addition to retrieving context from vector database, search modules intergrates data from other sources such as search engines, tabular data, knowledge graphs etc.
# Fusion — involves parallel vector searches of both original and expanded queries, intelligent reranking to optimize results, and pairing the best outcomes with new queries.
import pinecone
from langchain.vectorstores import Chroma
from langchain.vectorstores import Pinecone as PineconeVectorStore
from elasticsearch import Elasticsearch
import numpy as np

def retrieve_from_chroma(query_vector, metric='cosine', top_k=5, collection_name='default_collection'):
    """
    Retrieves the top_k most similar vectors from Chroma collection using the specified metric.
    
    Parameters:
    - query_vector: list, the query vector for which to find similar vectors.
    - metric: str, the similarity metric to use ('cosine', 'euclidean', 'manhattan').
    - top_k: int, the number of top similar results to retrieve.
    - collection_name: str, the name of the collection to use or create if none exist.
    
    Returns:
    - results: list of dictionaries, each containing the id and similarity score of the retrieved vectors.
    """
    chroma_db = Chroma(
        collection_name=collection_name,
    )
    if metric not in ['cosine', 'euclidean', 'manhattan']:
        raise ValueError("Unsupported metric. Choose from 'cosine', 'euclidean', 'manhattan'.")

    metric_map = {
        'cosine': 'cosine',
        'euclidean': 'l2',
        'manhattan': 'l1'
    }
    
    results = chroma_db.similarity_search_with_score(
        query_vector=query_vector,
        k=top_k,
        distance_metric=metric_map[metric]
    )

    return results


def retrieve_from_pinecone(query_vector, index_name, metric="cosine", top_k=5, ):
    """
    Retrieves the top_k most similar vectors from the Pinecone index using the specified metric.
    
    Parameters:
    - query_vector: list, the query vector for which to find similar vectors.
    - metric: str, the similarity metric to use ('cosine', 'euclidean', 'dotproduct').
    - top_k: int, the number of top similar results to retrieve.
    
    Returns:
    - results: list of dictionaries, each containing the id and similarity score of the retrieved vectors.
    """        
    index = pinecone.Index(index_name)
    
    response = index.query(
        vectors=query_vector,
        top_k=top_k,
        include_values=True,
        include_metadata=True
    )
    
    results = []
    for match in response['matches']:
        results.append({
            'id': match['id'],
            'score': match['score'],
            'metadata': match.get('metadata', {})
        })

    return results

def retrieve_from_elasticsearch(es_store, query_vector, metric='cosine', top_k=5):
    """
    Retrieves the top_k most similar vectors from Elasticsearch using the specified metric.
    
    Parameters:
    - es_store: ElasticsearchStore, the initialized Elasticsearch vector store.
    - query_vector: list, the query vector for which to find similar vectors.
    - metric: str, the similarity metric to use ('cosine', 'dotproduct', 'l2').
    - top_k: int, the number of top similar results to retrieve.
    
    Returns:
    - results: list of dictionaries, each containing the id and similarity score of the retrieved vectors.
    """
    if metric not in ['cosine', 'dotproduct', 'l2']:
        raise ValueError("Unsupported metric. Choose from 'cosine', 'dotproduct', 'l2'.")

    query_vector = np.array(query_vector).reshape(1, -1)  # Ensure it's a 2D array

    if metric == 'cosine':
        query = {
            "size": top_k,
            "query": {
                "knn": {
                    "field": "vector",
                    "query_vector": query_vector[0].tolist(),
                    "k": top_k,
                    "num_candidates": top_k * 10
                }
            }
        }
    elif metric == 'dotproduct':
        query = {
            "size": top_k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "dotProduct(params.query_vector, 'vector') + 1.0",
                        "params": {"query_vector": query_vector[0].tolist()}
                    }
                }
            }
        }
    elif metric == 'l2':
        query = {
            "size": top_k,
            "query": {
                "function_score": {
                    "query": {"match_all": {}},
                    "boost_mode": "replace",
                    "script_score": {
                        "script": {
                            "source": "1 / (1 + l2norm(params.query_vector, 'vector'))",
                            "params": {"query_vector": query_vector[0].tolist()}
                        }
                    }
                }
            }
        }
    
    es = Elasticsearch()
    index_name = es_store.index_name  
    response = es.search(index=index_name, body=query)

    results = []
    for hit in response['hits']['hits']:
        results.append({
            'id': hit['_id'],
            'score': hit['_score'],
            'source': hit['_source']
        })

    return results

