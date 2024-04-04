from langchain_doc_intelligence.AzureAIDocumentIntelligenceLoader import AzureAIDocumentIntelligenceLoader
from dotenv import load_dotenv
import os


load_dotenv()
endpoint = os.getenv('AZURE_DOC_INT_ENDPOINT')
key = os.getenv('AZURE_DOC_INT_ENDPOINT_KEY')

url_path  = "https://arxiv.org/pdf/2312.06648.pdf"


loader = AzureAIDocumentIntelligenceLoader(
    api_endpoint=endpoint, 
    api_key=key, 
    url_path =url_path, 
    api_model="prebuilt-layout",
    # mode="markdown"
    mode="markdown-page"
    # mode="page"
)

documents = loader.load()


# METHOD 1
# print(documents)

# METHOD 2
# i = 1

# for document in documents:
#     print(f"Page Content {i}: {document.page_content}")
#     print(f"Metadata {i}: {document.metadata}")
#     i = i + 1
