from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda
from filehistory import FileChatMessageHistory,get_chat_history
from vectorService import  VectorStoreService
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
import config_data
from operator import itemgetter
class RagService(object):
    def __init__(self):
        self.vector_service=VectorStoreService(
            embedding_model=config_data.embedding_model
        )
        self.prompt_template=ChatPromptTemplate.from_messages(
            [
                ("system","你是我的人工智能助手，协助我回答问题,现在有一些相关的文档内容可以参考：{Data}"),
                ("system","请结合这些历史会话记录回答"),
                MessagesPlaceholder("history"),
                ("human","根据上面提供的文档内容，回答以下问题：{question}"),
            ]
        )
        self.chat_model=None
        self.chain=self.__get_chain()
    def __format_doc(self,docs:list[Document]):
        res=""
        for doc in docs:
            res+=f"{doc.page_content}"
        return res
    '''from operator import itemgetter
  
    getter = itemgetter("question")  # 创建一个itemgetter对象,它会从输入的字典中提取键为"question"的值
    print(type(getter))  # <class 'operator.itemgetter'>
    print(callable(getter))  # True

    d = {"question": "鸣潮好玩吗？", "history": []}
    print(getter(d))  # 鸣潮好玩吗？
    '''

    def __get_chain(self):
        retriever=self.vector_service.get_retriever()
        model=ChatTongyi(model=config_data.chat_model)
        chain = {
                    "question": itemgetter("question"),
                    "Data": itemgetter("question") | retriever | self.__format_doc,
                    "history": itemgetter("history"),
                } | self.prompt_template | model | StrOutputParser()
        last_chain = RunnableWithMessageHistory(
            chain,
            get_chat_history,
            input_messages_key="question",#用户输入的键的名称
            history_messages_key="history",  # 模板中的history参数会被替换为这个key对应的消息历史记录，
            # 而这个消息记录是通过get_chat_history函数获取的，
            # get_chat_history函数会根据session_id返回对应的消息历史记录，这样就实现了不同用户之间的对话历史隔离
        )
        return last_chain
if __name__=="__main__":
    session_config={"configurable":{"session_id":"user_001"}}
    rag_service=RagService()
    question="鸣潮是一款好玩的游戏吗？"
    res=rag_service.chain.invoke({"question":question},config=session_config)
    #实际上传给链的内容是{question:,history:}，其中question是用户输入的问题，history是通过get_chat_history函数获取的这个session_id对应的消息历史记录
    print(res)


    question1="为什么鸣潮好玩？"
    res1=rag_service.chain.invoke({"question":question1},config=session_config)
    print(res1)

    question2="鸣潮的玩法是什么？"
    res2=rag_service.chain.invoke({"question":question2},config=session_config)
    print(res2)