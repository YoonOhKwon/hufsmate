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
        "- 특수 기호 사용 금지.\n"import os
from openai import OpenAI

API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com/v1"
)

def ai_solve(prompt: str, text: str) -> str:
    """
    prompt: 추가 조건(예: '정답만', '단계별로', '짧게', '수식 포함', '예시 포함' 등)
    text: 사용자가 낸 문제 본문(선택지/코드/표 등 포함 가능)
    """
    if not API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY 환경 변수가 설정되어 있지 않습니다.")

    system_instruction = (
        "너는 'AI 문제 풀이 및 해설 도우미'다.\n"
        "사용자가 제시한 문제(질문)에 대해 정확한 정답을 먼저 제시하고, 이어서 핵심 근거와 풀이를 간결하게 설명한다.\n"
        "문제가 객관식이면 선택지를 유지한 채 정답 번호/문자를 말하고, 주관식이면 결론을 한 문장으로 먼저 말한다.\n"
        "사용자가 추가로 조건(난이도, 답변 길이, 수식 사용, 예시 요구 등)을 주면 그 조건을 최우선으로 따른다.\n"
        "불확실하거나 정보가 부족하면 추측하지 말고, 어떤 정보가 부족한지 짧게 말한 뒤 가능한 범위에서 설명한다.\n"
        "출력 형식:\n"
        "정답: ...\n"
        "해설: ...\n"
        "단, 사용자가 '정답만'을 요구하면 해설을 생략한다.\n"
        "불필요한 인사말/자기소개는 금지한다.\n"
    )

    user_content = f"추가 조건: {prompt}\n\n문제:\n{text}"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


# (선택) 기존 이름을 유지하고 싶으면 래퍼로 연결
def ai_summarize(prompt: str, text: str) -> str:
    return ai_solve(prompt, text)

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

