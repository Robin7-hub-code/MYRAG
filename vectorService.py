import config_data
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
class VectorStoreService(object):
    def __init__(self, embedding_model="text-embedding-v4"):
        self.embedding_model=DashScopeEmbeddings(model=embedding_model)
        self.vector_store = Chroma(
            collection_name=config_data.collection_name,
            embedding_function=self.embedding_model,
            persist_directory=config_data.persist_directory
        )
    def get_retriever(self):
        retriever=self.vector_store.as_retriever(search_kwargs={"k":config_data.similarity_search_k})
        return retriever
