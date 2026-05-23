import os

os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

def load_dashscope_api_key():
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if api_key:
        return api_key

    try:
        import streamlit as st

        return st.secrets.get("DASHSCOPE_API_KEY")
    except Exception:
        return None


DASHSCOPE_API_KEY = load_dashscope_api_key()

if DASHSCOPE_API_KEY:
    os.environ["DASHSCOPE_API_KEY"] = DASHSCOPE_API_KEY

md5_path= 'md5.txt'
#Chroma数据库的collection_name和persist_directory参数配置
collection_name='text_collection'
persist_directory="./chroma_db"

#文本分割器的参数配置
chunk_size=200
chunk_overlap=20
separators=["\n\n","\n", " ", ""]
#vectorstore相似度搜索的参数配置
similarity_search_k=10
#模型的参数配置
embedding_model="text-embedding-v4"
chat_model="qwen3-max"
#历史记录的参数配置
session_config={"configurable":{"session_id":"user_001"}}
#local文件路径配置
local_file_path=["graphicdata/test.txt","graphicdata/STL源码剖析.pdf"]