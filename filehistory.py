import json,os
from typing import Sequence

from langchain_community.chat_models import ChatTongyi
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import messages_from_dict, message_to_dict, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, storage_path,session_id:str):
        self.storage_path=storage_path
        self.session_id=session_id
        self.fullpath=os.path.join(self.storage_path,self.session_id)
        os.makedirs(os.path.dirname(self.fullpath), exist_ok=True)
    @property
    def messages(self)->list[BaseMessage]:
        try:
            fullpath=os.path.join(self.storage_path,self.session_id)
            with open(fullpath,"r",encoding="utf-8") as f:
                message_data = json.load(f)
            return messages_from_dict(message_data)
        except FileNotFoundError:
            return []
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        fullpath = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(fullpath), exist_ok=True)
        added_messages = list(self.messages)
        added_messages.extend(messages)#此时的added_messages包含了之前的消息和新添加的消息,是列表的形式
        dict_messages = [message_to_dict(m) for m in added_messages]#把消息对象转换为字典形式,以便于存储为json格式
        with open(fullpath, "w", encoding="utf-8") as f:
            json.dump(dict_messages, f, ensure_ascii=False, indent=4)
    def clear(self) -> None:
        fullpath = os.path.join(self.storage_path, self.session_id)
        with open(fullpath, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)



model = ChatTongyi(model="qwen-plus")
prompt = PromptTemplate.from_template("根据会话历史回答问题，历史会话：{history}，问题：{input}，请给出答案")
base_chain = prompt  | model | StrOutputParser()


def get_chat_history(sessin_id):
   return FileChatMessageHistory(storage_path="./chat_history",session_id=sessin_id)

last_chain = RunnableWithMessageHistory(
    base_chain,
    get_chat_history,
    input_messages_key="input",
    history_messages_key="history",#模板中的history参数会被替换为这个key对应的消息历史记录，
    # 而这个消息记录是通过get_chat_history函数获取的，
    # get_chat_history函数会根据session_id返回对应的消息历史记录，这样就实现了不同用户之间的对话历史隔离
)

if __name__ == "__main__":
    session_config = {"configurable": {"session_id": "user_001"}}  # 每个用户一个session_id,用来区分不同用户的对话历史

    print("第一轮对话：")
    response1 = last_chain.invoke({"input": "小明有一只猫"}, session_config)
    # seeion_id为user_001的用户的消息历史记录中会记录这次对话，下一次对话时会把这次对话作为历史传入模型，这样模型就能记住之前的对话内容，实现上下文关联
    print(response1)

    print("\n第二轮对话：")
    response2 = last_chain.invoke({"input": "小亮有一只狗"}, session_config)
    print(response2)

    print("\n第三轮对话（测试记忆）：")
    response3 = last_chain.invoke({"input": "小明和小亮的宠物一共有几只"}, session_config)
    print(response3)
