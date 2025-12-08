import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com/v1"
)



def ai_summarize(prompt : str, text: str) -> str:
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": (
                    
                    str(prompt) +
                    "공지 내용을 요약하라. 한국어를 사용하고, 영어로 이루어진 공지라면 한국어로 번역해서 출력하라. "
                    "불필요한 인사말, 자기소개, 설명은 절대 포함하지 마라. "
                    "링크를 제공한다면, 요약 내부 또는 밑에 반드시 첨부하라."
                    "형식을 통일하라."
                    "기호 사용을 하지마라."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    return response.choices[0].message.content


