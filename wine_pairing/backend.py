import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv('OPENAI_API_KEY'),
    max_tokens=4096,
)

def recommend_food(query: str, image_urls: list = None):
    with open('system_prompt_1.md') as f:
        system_prompt = f.read()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{text}"),
    ])

    template = []
    if image_urls:
        template += [{'image_url': {'url': image_url}} for image_url in image_urls]
    template += [{'text': query}]
    prompt += HumanMessagePromptTemplate.from_template(template=template)

    return prompt | llm | StrOutputParser()