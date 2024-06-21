import langchain



def ensembler(pinecone_retriever, elastic_retriever, user_query):
    ensemble_retriever = langchain.EnsembleRetriever([pinecone_retriever, elastic_retriever], weights=[0.5, 0.5])
    retrieved_data = ensemble_retriever.retrieve(user_query)
    return retrieved_data



    