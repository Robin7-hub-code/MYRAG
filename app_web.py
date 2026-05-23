import streamlit as st
import time
import config_data
from rag import RagService
from streamlit import session_state
from base_knowledge import KnowledgeService
def catch_cache(iterator,cache:list):
    for res in iterator:
        cache.append(res)
        yield res

#  streamlit run app_web.py
st.title("STL专家")
st.divider()

#文件上传功能
st.subheader("增加相关知识")
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["txt","pdf"],
    accept_multiple_files=False,
)
#session_state初始化，存储知识库服务对象、RAG服务对象和消息列表
if "service"not in st.session_state:
    st.session_state["service"] = KnowledgeService()
    st.session_state["service"].load_local_file()  # 加载本地文件到知识库中

if session_state.get("rag_service") is None:
   session_state["rag_service"] = RagService()

if session_state.get("message") is None:
    session_state["message"] = []




if uploaded_file is not None:
    file_name=uploaded_file.name
    with st.spinner("Uploading file..."):
        time.sleep(1)
        text = uploaded_file.getvalue().decode("utf-8")
        st.session_state["service"].upload_file_web(text,file_name)
        st.write("文件上传成功！")



prompt=st.chat_input()
#设置输入框，获得用户输入
if session_state.get("message") is not None:
    for message in session_state["message"]:
      st.chat_message(message["role"]).write(message["content"])

if prompt :
    st.chat_message("user").write(prompt)
    session_state["message"].append({"role": "user", "content": prompt})
    with st.spinner("正在思考..."):
        res=st.session_state["rag_service"].chain.stream({"question": prompt}, config=config_data.session_config)
        cache=[]
        st.chat_message("assistant").write_stream(catch_cache(res,cache))
        session_state["message"].append({"role": "assistant", "content": ''.join(cache)})