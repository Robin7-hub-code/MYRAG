import os
from langchain_core.documents import Document
import config_data
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader,PyPDFLoader
#检查文件是否被保存过
def check_md5(md5_str:str):
    if not os.path.exists(config_data.md5_path):
        open(config_data.md5_path, "w", encoding='utf-8').close()
        print("创建md5文件成功")
        return False
    else:
         for line in open(config_data.md5_path, "r", encoding='utf-8').readlines():
             line = line.strip()
             if line == md5_str:
                 return True
    return False
#保存文件的md5值
def save_md5(md5_str:str):
    if not os.path.exists(config_data.md5_path):
        open(config_data.md5_path, "w", encoding='utf-8').close()
        print("创建md5文件成功")
    with open(config_data.md5_path, "a", encoding='utf-8') as f:
         f.write(md5_str + "\n")
    pass
#将字符串转换成md5字符串值
def get_str_to_md5(input_str:str,encoding='utf-8'):
    strBytes = input_str.encode(encoding=encoding)
    md5 = hashlib.md5()#创建md5对象
    md5.update(strBytes)#更新md5对象
    md5_str = md5.hexdigest()#获取md5字符串值
    return md5_str
def get_documents_to_md5(documents:list[Document],encoding='utf-8'):
    strBytes = "".join([doc.page_content for doc in documents]).encode(encoding=encoding,errors='ignore')
    md5 = hashlib.md5()#创建md5对象
    md5.update(strBytes)#更新md5对象
    md5_str = md5.hexdigest()#获取md5字符串值
    return md5_str

class KnowledgeService(object):
   def __init__(self):
       os.makedirs(config_data.persist_directory, exist_ok=True)
       self.chroma=Chroma(
           collection_name=config_data.collection_name,
           embedding_function=DashScopeEmbeddings(model='text-embedding-v4'),
           persist_directory=config_data.persist_directory
       )#向量数据库
       self.spliter=RecursiveCharacterTextSplitter(
              chunk_size=config_data.chunk_size,
              chunk_overlap=config_data.chunk_overlap,
              separators=config_data.separators,
              length_function=len,
       )#文本分割器
  #将传入的字符串转换为向量并保存到数据库中
   def upload_file_web(self,data:str,file_name):
        md5_str=get_str_to_md5(data)
        if check_md5(md5_str):
            print("文件已存在")
        else:
            print("文件不存在")
            save_md5(md5_str)
            #文本分割
            if len(data)>1000 :
                split_docs=self.spliter.split_text(data)
            else:
                split_docs=[data]

            self.chroma.add_texts(
                split_docs,
                ids=[md5_str+"id"+str(i) for i in range(len(split_docs))],

            )
        print("成功上传文件到知识库")
   #离线文件上传，传入Document对象列表
   def upload_file_after(self,data:list[Document],file_name):
       # 清理非法代理字符
        for doc in data:
           doc.page_content = doc.page_content.encode('utf-8', errors='ignore').decode('utf-8')
        md5_str=get_documents_to_md5(data)
        if check_md5(md5_str):
            print("文件已存在")
            return True
        else:
            print("文件不存在")
            save_md5(md5_str)
            #文本分割
            split_docs=self.spliter.split_documents(data)
            self.chroma.add_documents(
                split_docs,
                ids=[md5_str+"id"+str(i) for i in range(len(split_docs))],
            )
            return False
   def loadTex(self,path:str,encoding='utf-8'):
        loader=TextLoader(
            file_path=path,
            encoding=encoding
        )
        documents=loader.load()
        return documents
   def loadpdf(self,path:str,mymode='page'):
        loader=PyPDFLoader(
            file_path=path,
            mode=mymode,
        )
        documents=loader.load()
        return documents
   def load_local_file(self,path:list[str]=config_data.local_file_path,encoding='utf-8'):
       for pt in path:
            ext = os.path.splitext(pt)[1].lower()
            if ext=='.pdf':
                documents=self.loadpdf(pt)
                if len(documents)==0:
                    print(f"pdf文件'{pt}'加载失败，未提取到内容")
                    continue
                print("pdf文件加载成功")
            elif ext=='.txt':
                documents=self.loadTex(pt,encoding)
            else:
                raise ValueError(f"不支持的文件类型: '{ext}'，仅支持 .txt 和 .pdf")
            self.upload_file_after(documents, pt)
            print(pt+"上传成功")
if __name__ == '__main__':
   service=KnowledgeService()
   service.upload_file_web("这是一个测试文本","test.txt")
