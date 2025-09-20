from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import create_react_agent
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.messages import HumanMessage
from typing import List
from langgraph.graph import START, END
from pydantic import BaseModel

load_dotenv() # OPENAI_API_KEY, PINECONE_API_KEY

llm = ChatOpenAI(model="gpt-4.1", temperature=0)
small_llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = PineconeVectorStore(
    index_name="inhouse-rule-index",
    embedding=embeddings,
)
retriever = vector_store.as_retriever()

graph_builder = StateGraph(MessagesState)

class CheckFaqResponse(BaseModel):
    is_in_faq: bool
    context: list[Document]

@tool
def check_faq(question: str) -> CheckFaqResponse:
    """Check if the question is in the FAQ.
    If the question is in the FAQ, return the context of the question.
    Otherwise, return an empty list.
    """

    # context = retriever.invoke(question, filter={"source": "employee_benefits_and_welfare_faq"})
    context = retriever.invoke(question)
    check_faq_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that checks if the question is in the FAQ. If the question is in the FAQ, return 'Yes'. Otherwise, return 'No'."""),
        ("user", "Question: {question}\nContext: {context}"),
    ])
    check_faq_chain = check_faq_prompt | llm | StrOutputParser()
    is_in_faq = check_faq_chain.invoke({"question": question, "context": context})
    return {"is_in_faq": is_in_faq == "Yes", "context": context if is_in_faq == "Yes" else []}

@tool
def get_document_name(question: str) -> str:
    """Get the document name based on the question."""

    determine_document_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", """You are a helpful assistant that determines the most relevant document name based on the user's question. 
Choose from the following document names:
- delegation_of_authority
- employee_benefits_and_welfare_faq
- employee_benefits_and_welfare_guide
- employee_handbook_and_hr_policy
- expense_management_guide
- it_support_guide
- legal_and_compliance_policy

Return ONLY the document name (e.g., 'it_support_guide').

Examples:
- If the question is about who can approve expenses, return 'delegation_of_authority' or 'expense_management_guide' as appropriate.
- If the question is about employee benefits, return 'employee_benefits_and_welfare_guide'.
- If the question is about HR policies or the employee handbook, return 'employee_handbook_and_hr_policy'.
- If the question is about IT support or technical issues, return 'it_support_guide'.
- If the question is about legal or compliance matters, return 'legal_and_compliance_policy'.
- If the question is a frequently asked question about benefits, return 'employee_benefits_and_welfare_faq'.
"""),
        ("user", "Question: {question}"),
    ]
)

    determine_document_chain = determine_document_prompt | small_llm | StrOutputParser()
    document_name = determine_document_chain.invoke({"question": question})
    return document_name

@tool
def retriever_tool(question: str, document_name: str) -> List[Document]:
    """Retrieve the document based on the question and document name."""

    context = retriever.invoke(question, filter={"source": document_name})
    return context

# retriever_tool = create_retriever_tool(
#     retriever, 
#     "company_document_retriever",
#     """사내 문서 모음에서 정보를 찾아주는 도구입니다. 문서 이름을 기반으로 source에 필터링을 한 후에, page_content를 반환합니다."""
# )

agent = create_react_agent(
    model="openai:gpt-4.1",
    tools=[retriever_tool, check_faq, get_document_name],
    prompt="Use the tools provided to you to answer the user's question",
)

for chunk in agent.stream({"messages": [HumanMessage(content="사내 네트워크 담당자는 누구인가요?")]}, stream_mode="values"):
    chunk['messages'][-1].pretty_print()