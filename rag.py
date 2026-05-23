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
                ("system",
                 "你是一位专业的 STL（C++ 标准模板库）技术专家助手，擅长解答 STL 源码、数据结构与算法相关问题。\n\n"
                 "## 参考知识库\n"
                 "以下是从知识库中检索到的与问题最相关的文档片段，请优先基于这些内容作答：\n"
                 "```\n{Data}\n```\n\n"
                 "## 回答规范\n"
                 "1. 若知识库内容足以回答问题，请严格依据知识库内容作答，并在回答末尾注明「来源：知识库」。\n"
                 "2. 若知识库内容不足，可结合你自身的专业知识补充，但须明确说明哪部分来自知识库、哪部分来自模型推断。\n"
                 "3. 回答请条理清晰，对代码相关问题给出示例；对概念性问题给出简洁定义后再展开解释。\n"
                 "4. 如果问题与 STL 或 C++ 无关，礼貌地提示用户本助手专注于 STL 领域。"
                ),
                ("system", "## 历史会话\n请结合以下对话历史理解用户的上下文意图："),
                MessagesPlaceholder("history"),
                ("human", "{question}"),
            ]
        )
        self.chat_model=None
        self.chain=self.__get_chain()
    def __format_doc(self, docs: list[Document]):
        if not docs:
            return "（未检索到相关文档，请依据自身知识回答）"
        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "未知来源")
            page   = doc.metadata.get("page", "")
            loc    = f"{source}" + (f" 第{page}页" if page != "" else "")
            parts.append(f"【片段{i} | {loc}】\n{doc.page_content.strip()}")
        return "\n\n".join(parts)
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