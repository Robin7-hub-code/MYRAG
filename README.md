# MYRAG（Streamlit Cloud 部署说明）

本项目可部署为 Streamlit Cloud Web 应用，主入口文件为：

- `app_web.py`

## 1. 部署到 Streamlit Cloud

1. 打开 https://share.streamlit.io 并使用 GitHub 登录。
2. 点击 **New app**。
3. 选择仓库：`Robin7-hub-code/MYRAG`
4. 选择分支：`master`
5. **Main file path** 填写：`app_web.py`
6. 点击 **Deploy!**

项目依赖已写在 `requirements.txt`，Streamlit Cloud 会自动安装。

## 2. 配置密钥（必须）

本项目使用通义千问，需要配置 `DASHSCOPE_API_KEY`。

在 Streamlit Cloud 应用页进入 **Settings → Secrets**，填写：

```toml
DASHSCOPE_API_KEY = "你的通义千问API Key"
```

代码会按以下顺序读取密钥：
1. 环境变量 `DASHSCOPE_API_KEY`
2. Streamlit Secrets `st.secrets["DASHSCOPE_API_KEY"]`

若未配置，应用会在页面给出错误提示并停止运行。

## 3. 关于知识库与本地文件

- `chroma_db/`、`graphicdata/`、`chat_history/`、`md5.txt` 已配置为本地/生成文件，不应提交到仓库。
- 云端首次部署通常没有本地向量库数据，需要在页面上传文档后重新构建知识库。
- 若 `config_data.py` 中配置的本地文件在云端不存在，程序会自动跳过，不会阻塞启动。
