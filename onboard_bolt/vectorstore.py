import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone.vectorstores import PineconeVectorStore

load_dotenv()

index_name = "onboard-bolt"
embedding = OpenAIEmbeddings(
    model='text-embedding-3-small',
    api_key=os.getenv('OPENAI_API_KEY'),
)
vectorstore = PineconeVectorStore(
    embedding=embedding,
    index_name=index_name,
    pinecone_api_key=os.getenv('PINECONE_API_KEY'),
)


class CustomLoader:
    
    def load(self):
        loader = TextLoader("docs/onboarding.txt", encoding='utf-8')
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

        split_docs = text_splitter.split_documents(documents)

        vectorstore.add_documents(
            documents=split_docs
        )


if __name__ == '__main__':
    # loader = CustomLoader()
    # loader.load()

    ############################

    # vectorstore에 저장된 데이터를 검색합니다.

    # 방법 1. similarity_search 메서드 사용
    # vectorstore.similarity_search('육아 휴직 신청 방법을 알려주세요.', k=5)

    # 방법 2. as_retriever LCEL 사용
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    response = retriever.invoke('육아 휴직 신청 방법을 알려주세요.')
    print(response)