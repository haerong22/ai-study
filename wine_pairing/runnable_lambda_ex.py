import os

from openai import OpenAI
from dotenv import load_dotenv

from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def openai_response(query, image_urls=None):
    """
    참고정보
    https://python.langchain.com/v0.2/docs/how_to/lcel_cheatsheet/#get-all-prompts-in-a-chain
    """
    if image_urls:
        content = [
            {"type": "image_url", "image_url": {"url": image_url}}
            for image_url in image_urls
        ]
    content += [{"type": "text", "text": query}]

    with open('system_prompt_1.md') as f:
        system_prompt = f.read()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": content
            }
        ],
        temperature=0,
        max_tokens=4095,
        top_p=0,
        frequency_penalty=0,
        presence_penalty=0
    )
    return ''.join([c.message.content for c in response.choices])


def AI_sommelier(query, image_urls=None):
    runnable = RunnableLambda(openai_response)
    bound_runnable = runnable.bind(image_urls=image_urls)
    chain = bound_runnable | StrOutputParser()
    return chain.invoke(query)


if __name__ == '__main__':
    response = AI_sommelier(
        query = "이 와인에 어울리는 음식은 무엇인가요?",
        image_urls=["https://images.vivino.com/thumbs/GpcSXs2ERS6niDxoAsvESA_pb_x600.png"],
    )
    print(response)

# 이 와인은 나파 밸리의 카베르네 소비뇽입니다. 일반적으로 카베르네 소비뇽은 풍부한 과일 향과 강한 탄닌 구조를 가지고 있어, 다음과 같은 음식과 잘 어울립니다:

# 1. **스테이크**: 특히 리브아이 같은 기름진 부위가 좋습니다.
# 2. **양고기**: 허브와 함께 구운 양고기 요리.
# 3. **치즈**: 에이지드 체다나 블루 치즈.
# 4. **버섯 요리**: 포르치니 버섯 리조또.

# 이 와인의 풍부한 맛과 구조가 이러한 음식들과 잘 어우러질 것입니다.