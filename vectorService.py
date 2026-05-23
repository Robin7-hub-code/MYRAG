import config_data
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings

class VectorStoreService(object):
    def __init__(self, embedding_model="text-embedding-v4"):
        self.embedding_model = DashScopeEmbeddings(model=embedding_model)
        self.vector_store = Chroma(
            collection_name=config_data.collection_name,
            embedding_function=self.embedding_model,
            persist_directory=config_data.persist_directory
        )

    def get_retriever(self):
        """
        使用 MMR（最大边际相关性）策略检索：
        - fetch_k: 先从向量库召回的候选数量（越大召回越广）
        - k:       最终返回给模型的片段数量
        - lambda_mult: 多样性权重，0=最大多样性，1=最大相关性，推荐 0.5~0.7
        """
        retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": config_data.similarity_search_k,
                "fetch_k": config_data.similarity_search_k * 3,
                "lambda_mult": 0.6,
            }
        )
        return retriever
