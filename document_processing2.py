from langchain_doc_intelligence.AzureAIDocumentIntelligenceLoader import AzureAIDocumentIntelligenceLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant

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
    mode="markdown-page"
)

documents = loader.load()

headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
chunks = []

for doc in documents:
    chunks.extend(markdown_splitter.split_text(doc.page_content))


embeddings = OpenAIEmbeddings()
# chunk_embeddings = [embeddings.embed_documents([chunk.page_content]) for chunk in chunks]


qdrant = Qdrant.from_documents(
    chunks, embeddings,
    # location="/data", 
    # location="R:/Work/Asoft/doc-intelligence/langchain",
    url="http://localhost:6333",
    collection_name="markdown_chunks"
)

print("Qdrant vector store created successfully")

#better chunking logic?

# chunks = []
# for doc in documents:
#     # Split the document by "Section" headers first
#     section_chunks = markdown_splitter.split_text(doc.page_content, headers_to_split_on=[("#", "Section")])

#     for section_chunk in section_chunks:
#         # Split each section by "Subsection" headers
#         subsection_chunks = markdown_splitter.split_text(section_chunk.page_content, headers_to_split_on=[("##", "Subsection")])

#         # Update the metadata for each subsection chunk
#         for subsection_chunk in subsection_chunks:
#             subsection_chunk.metadata.update(section_chunk.metadata)

#         chunks.extend(subsection_chunks)










# Retrieve all the chunks from the Qdrant vector store

# all_chunks = qdrant.get_all_documents()

# # Print the content and metadata of each chunk
# for chunk in all_chunks:
#     print(f"Content: {chunk.page_content}")
#     print(f"Metadata: {chunk.metadata}")
#     print("-" * 20)

# similarity search 

# from langchain_openai import OpenAIEmbeddings

# # Create embeddings for the query
# embeddings = OpenAIEmbeddings()
# query_embedding = embeddings.embed_query("your query text here")

# # Perform similarity search
# similar_chunks = qdrant.similarity_search(query_embedding, k=5)

# # Print the most similar chunks
# for chunk in similar_chunks:
#     print(f"Content: {chunk.page_content}")
#     print(f"Metadata: {chunk.metadata}")
#     print("-" * 20)