import pypdf
from langchain_community.document_loaders import TextLoader,PyPDFLoader

loader=PyPDFLoader(
      "./graphicdata/06-Drawing_Things.pdf",
      mode='page'
)
documents=loader.load()
for document in documents:
    document.page_content=document.page_content.encode("utf8",errors="ignore").decode("utf8")
    print(document.page_content)
