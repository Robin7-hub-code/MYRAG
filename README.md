# MYRAG（Streamlit Cloud 部署说明）

本项目可部署为 Streamlit Cloud Web 应用，主入口文件为：

- `app_web.py`

## 1. 部署到 Streamlit Cloud

1. 打开 https://share.streamlit.io ，点击 **Continue with GitHub** 并完成授权登录。
2. 点击右上角 **New app**。
3. 在部署表单中填写：
   - **Repository**：`Robin7-hub-code/MYRAG`
   - **Branch**：`master`
   - **Main file path**：`app_web.py`
4. 点击 **Deploy!**
5. 等待 2 到 5 分钟，部署成功后会生成类似 `https://xxx.streamlit.app` 的访问链接。

项目依赖已写在 `requirements.txt`，Streamlit Cloud 会自动安装。

## 2. 配置密钥（必须）

本项目使用通义千问，需要配置 `DASHSCOPE_API_KEY`。

在 Streamlit Cloud 应用页进入 **Manage app → Settings → Secrets**，填写：

```toml
DASHSCOPE_API_KEY = "你的通义千问API Key"
```

代码会按以下顺序读取密钥：
1. 环境变量 `DASHSCOPE_API_KEY`
2. Streamlit Secrets `st.secrets["DASHSCOPE_API_KEY"]`

若未配置，应用会在页面给出错误提示并停止运行。
请不要把 API Key 直接写死在代码里。

## 3. 关于知识库与本地文件

- `chroma_db/`、`graphicdata/`、`chat_history/`、`md5.txt` 已配置为本地/生成文件，不应提交到仓库。
- 云端首次部署通常没有本地向量库数据，因此**不要上传本地 `chroma_db/`**，部署后在页面重新上传文档即可。
- 侧边栏支持上传 `txt` / `pdf` 文件；上传成功后会自动写入云端当前运行环境中的知识库。
- 若 `config_data.py` 中配置的本地文件在云端不存在，程序会自动跳过，不会阻塞启动。

## 4. 部署后的首次使用

1. 打开刚生成的 Streamlit Cloud 链接。
2. 确认页面未出现 `DASHSCOPE_API_KEY` 缺失提示。
3. 在左侧 **知识库管理** 区域上传 `txt` 或 `pdf` 文件。
4. 等待页面出现“上传成功”提示后，即可直接开始提问，无需额外点击其他按钮。

## 5. 常见问题排查

- **页面提示缺少 `DASHSCOPE_API_KEY`**：检查 Secrets 是否保存成功，并确认变量名完全一致。
- **部署安装依赖失败**：确认仓库根目录存在 `requirements.txt`，修改后可在 Streamlit Cloud 中重新部署。
- **可以打开页面，但回答没有知识库内容**：这是首次部署的正常现象，请先上传文档重建知识库。
- **首次打开速度较慢**：免费应用在长时间无访问后可能休眠，重新唤醒通常需要几十秒。
