import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from retrieval import wine_search

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv('OPENAI_API_KEY'),
    max_tokens=4096,
)

def taste_food(x):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """When provided with an input question, please identify the dish in question and describe what it tastes like."""),
    ])

    template = []
    if x['image_urls']:
        template += [{'image_url': {'url': image_url}} for image_url in x['image_urls']]
    template += [{'text': x['query']}]
    prompt += HumanMessagePromptTemplate.from_template(template=template)

    return prompt | llm | StrOutputParser()

def recommend_wine(x):
    with open('system_prompt.md') as f:
        system_prompt = f.read()
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
    ])
    return prompt | llm | StrOutputParser()

def recommend_food(x):
    with open('system_prompt_1.md') as f:
        system_prompt = f.read()

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{text}"),
    ])

    template = []
    if x['image_urls']:
        template += [{'image_url': {'url': image_url}} for image_url in x['image_urls']]
    template += [{'text': x['query']}]
    prompt += HumanMessagePromptTemplate.from_template(template=template)

    return prompt | llm | StrOutputParser()

def wine_retrieval(taste):
    return {'food': taste, 'reviews': '\n'.join(d.page_content for d in wine_search(taste))}


def chain_recommend_wine():
    return RunnableLambda(taste_food) | RunnableLambda(wine_retrieval) | RunnableLambda(recommend_wine)

def chain_recommend_food():
    return RunnableLambda(recommend_food)

if __name__ == '__main__':
    response = chain_recommend_wine().invoke({
        "query": "이 음식과 어울리는 와인을 추천해 주세요.",
        "image_urls": ["https://www.shutterstock.com/ko/blog/wp-content/uploads/sites/17/2018/11/shutterstock_1068672764.jpg"]
    })
    print(response)