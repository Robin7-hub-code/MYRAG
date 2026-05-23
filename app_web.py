import streamlit as st
import time
import uuid
import os
import config_data
from streamlit import session_state

# ── 页面基础配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="STL 专家",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not config_data.DASHSCOPE_API_KEY:
    st.error("未检测到 DASHSCOPE_API_KEY，请在环境变量或 Streamlit Secrets 中配置。")
    st.stop()

from rag import RagService
from base_knowledge import KnowledgeService

# ── 自定义样式 ────────────────────────────────────────────────
st.markdown("""
<style>
/* 隐藏默认的 Streamlit 页脚 */
footer {visibility: hidden;}
/* 聊天输入框固定底部效果优化 */
.stChatFloatingInputContainer { bottom: 1rem; }
/* 侧边栏标题 */
.sidebar-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; }
/* 对话列表按钮统一宽度 */
section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    text-align: left;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


# ── 工具函数 ──────────────────────────────────────────────────
def catch_cache(iterator, cache: list):
    for res in iterator:
        cache.append(res)
        yield res


def new_session_id() -> str:
    return f"session_{uuid.uuid4().hex[:8]}"


def get_session_label(sid: str, idx: int) -> str:
    """生成对话列表显示名称"""
    msgs = session_state["conversations"].get(sid, [])
    for m in msgs:
        if m["role"] == "user":
            text = m["content"][:20]
            return f"💬 {text}…" if len(m["content"]) > 20 else f"💬 {text}"
    return f"🆕 新对话 {idx + 1}"


# ── Session State 初始化 ──────────────────────────────────────
if "service" not in session_state:
    with st.spinner("正在加载知识库…"):
        session_state["service"] = KnowledgeService()
        session_state["service"].load_local_file()

if "rag_service" not in session_state:
    session_state["rag_service"] = RagService()

# 所有对话的 session_id 列表
if "session_ids" not in session_state:
    first_id = new_session_id()
    session_state["session_ids"] = [first_id]
    session_state["current_session"] = first_id
    session_state["conversations"] = {first_id: []}  # sid -> message list


# ── 侧边栏 ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 STL 专家")
    st.divider()

    # 新建对话按钮
    if st.button("➕ 新建对话", use_container_width=True, type="primary"):
        new_sid = new_session_id()
        session_state["session_ids"].append(new_sid)
        session_state["conversations"][new_sid] = []
        session_state["current_session"] = new_sid
        st.rerun()

    st.markdown("**历史对话**")

    # 对话列表
    for idx, sid in enumerate(reversed(session_state["session_ids"])):
        label = get_session_label(sid, idx)
        is_active = sid == session_state["current_session"]
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"sess_{sid}", use_container_width=True, type=btn_type):
            session_state["current_session"] = sid
            st.rerun()

    st.divider()

    # 知识库上传区域
    st.markdown("**📚 知识库管理**")
    uploaded_file = st.file_uploader(
        "上传文档（txt / pdf）",
        type=["txt", "pdf"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )
    if uploaded_file is not None:
        with st.spinner("正在上传并入库…"):
            time.sleep(0.5)
            if uploaded_file.type == "application/pdf":
                # PDF 以字节流方式保存后加载
                tmp_path = f"./graphicdata/{uploaded_file.name}"
                os.makedirs("./graphicdata", exist_ok=True)
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                session_state["service"].upload_file_web(tmp_path, uploaded_file.name)
            else:
                text = uploaded_file.getvalue().decode("utf-8")
                session_state["service"].upload_file_web(text, uploaded_file.name)
        st.success(f"✅ {uploaded_file.name} 上传成功！")

    st.divider()
    st.caption("Powered by LangChain & 通义千问")


# ── 主区域 ────────────────────────────────────────────────────
current_sid = session_state["current_session"]
current_messages = session_state["conversations"].get(current_sid, [])

# 标题
col1, col2 = st.columns([8, 2])
with col1:
    st.title("🤖 STL 专家助手")
    st.caption(f"当前对话 ID：`{current_sid}`")
with col2:
    if st.button("🗑️ 清空本对话", use_container_width=True):
        session_state["conversations"][current_sid] = []
        # 同时清空文件历史
        from filehistory import get_chat_history
        get_chat_history(current_sid).clear()
        st.rerun()

st.divider()

# 渲染历史消息
chat_container = st.container()
with chat_container:
    if not current_messages:
        st.markdown(
            "<div style='text-align:center;color:gray;margin-top:3rem;'>"
            "👋 你好！有什么关于 STL 的问题，尽管问我吧~"
            "</div>",
            unsafe_allow_html=True,
        )
    for message in current_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ── 输入框 ────────────────────────────────────────────────────
prompt = st.chat_input("请输入您的问题…")

if prompt:
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    session_state["conversations"][current_sid].append({"role": "user", "content": prompt})

    # 调用 RAG 并流式输出
    session_config = {"configurable": {"session_id": current_sid}}
    with st.chat_message("assistant"):
        with st.spinner("正在思考…"):
            res = session_state["rag_service"].chain.stream(
                {"question": prompt}, config=session_config
            )
            cache = []
            st.write_stream(catch_cache(res, cache))

    session_state["conversations"][current_sid].append(
        {"role": "assistant", "content": "".join(cache)}
    )
    st.rerun()
