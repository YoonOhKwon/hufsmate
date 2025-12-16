import os
from openai import OpenAI

API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com/v1"
)


def ai_summarize(prompt: str, text: str) -> str:

    system_instruction = (
        "너의 최우선 임무는 다음과 같다:\n"
        "1. 사용자가 제공한 추가 명령(prompt)을 가장 우선적으로 따른다.\n"
        "2. 만약 추가 명령과 그 다음 규칙이 충돌한다면, 추가 명령을 우선한다.\n\n"
        "추가 규칙:\n"
        "- 공지 내용을 한국어로 간결하게 요약하라.\n"
        "- 영어 공지가 있다면 자연스러운 한국어로 번역 포함.\n"
        "- 불필요한 설명, 인사말, 자기소개 금지.\n"
        "- 링크가 있다면 요약 하단에 포함.\n"
        "- 형식은 문장 단위로 통일.\n"
        "- 특수 기호 사용 금지.\n"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"추가 명령: {prompt}"},
            {"role": "user", "content": f"공지 내용:\n{text}"}
        ]
    )

    return response.choices[0].message.content

