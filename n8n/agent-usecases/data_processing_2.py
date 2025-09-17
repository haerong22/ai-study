from langchain_text_splitters import MarkdownHeaderTextSplitter
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import os

load_dotenv()

headers_to_split_on = [
    ("#", "title"),    
    ("##", "chapter"),    
    ("###", "section"),   
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

index_name = "inhouse-python-index"
vector_store = PineconeVectorStore(
    index_name=index_name,
    embedding=embeddings,
)

input_dir = './output'

for filename in os.listdir(input_dir):
    if filename.endswith('.md'):
        md_path = os.path.join(input_dir, filename)
        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
            
        docs = markdown_splitter.split_text(markdown_text)
        for doc in docs:
            doc.metadata['source'] = filename.replace('.md', '')
            print(doc)

        vector_store.add_documents(docs)

retriever = vector_store.as_retriever()

retriever.invoke("복리후생 및 복지 FAQ")