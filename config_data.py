import os
os.environ["DASHSCOPE_API_KEY"] = "sk-528a3b09bb8e440cbe29d7a315e10472"

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