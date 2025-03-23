# Streamlit + GPT 창의력 검사 프로그램

import streamlit as st
import pandas as pd
import re
import os

# openai 라이브러리 import 시 예외 처리
try:
    import openai
except ModuleNotFoundError:
    st.error("⚠️ openai 모듈이 설치되어 있지 않습니다.\nStreamlit Cloud의 Settings > Manage App > Packages 에서 `openai` 패키지를 추가해 주세요.")
    st.stop()

# OpenAI API 키 설정 (Streamlit Cloud의 secrets 사용 권장)
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# 문항 구성
questions = {
    "유창성": [
        "가능한 한 많은 둥근 물건을 말해보세요.",
        "비 오는 날에 할 수 있는 일을 최대한 많이 떠올려 보세요.",
        "책을 어떻게 쓰일 수 있는지 생각나는 대로 적어보세요.",
        "빨간색을 떠올리면 어떤 것들이 생각나나요?",
        "학교에서 볼 수 있는 물건을 가능한 한 많이 나열해 보세요."
    ],
    "융통성": [
        "얼음을 다른 용도로 사용할 수 있는 방법을 떠올려 보세요.",
        "자동차를 운전하지 않고도 다른 용도로 사용할 수 있는 방법은?",
        "연필을 쓰기 외에 쓸 수 있는 방법을 적어보세요.",
        "컵이 깨졌을 때 어떻게 활용할 수 있을까요?",
        "집이 없는 사람들을 위한 색다른 주거 형태를 상상해 보세요."
    ],
    "독창성": [
        "새로운 직업 하나를 만들어 이름과 설명을 적어보세요.",
        "당신이 발명할 수 있다면 어떤 새로운 물건을 만들고 싶나요?",
        "현실에는 없는 기상현상을 상상해 보세요.",
        "스마트폰이 지금보다 더 기발한 기능을 가진다면 무엇일까요?",
        "동화에 나오는 악당을 새롭게 만든다면 어떤 모습일까요?"
    ],
    "정교성": [
        "하늘을 나는 신발에 대해 구체적으로 설명해 보세요.",
        "당신이 만든 로봇 친구는 어떤 기능을 가지고 있나요?",
        "미래의 학교는 어떤 모습일지 자세히 그려보세요.",
        "새로운 놀이기구를 만든다면, 어떤 구조이고 어떻게 작동하나요?",
        "시간을 멈추는 시계가 있다면 어떻게 생겼고 어떻게 사용하나요?"
    ],
    "상상력": [
        "하늘에 떠 있는 도시는 어떤 모습일까요?",
        "당신이 동물이 될 수 있다면 어떤 동물이 되고 무엇을 하고 싶나요?",
        "색깔이 바뀌는 나무가 있다면 어떤 원리로 작동할까요?",
        "꿈에서 책 속 세상으로 들어간다면 무슨 일이 벌어질까요?",
        "미래의 지구가 물로 덮인 세상이라면 사람들은 어떻게 살까요?"
    ]
}

# GPT 채점 함수
def gpt_score(question, answer):
    prompt = f"""
    다음은 창의력 검사 문항에 대한 답변입니다:

    질문: {question}
    답변: {answer}

    이 답변을 아래 기준으로 평가해 주세요:
    - 창의성 (10점 만점): 새롭고 독창적인가?
    - 구체성 (10점 만점): 구체적으로 설명했는가?
    - 아이디어 수 (10점 만점): 다양한 아이디어를 언급했는가?

    각 항목에 점수를 부여하고 간단한 피드백을 주세요.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT 오류: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="GPT 창의력 검사", layout="wide")
st.title("🧠 GPT 기반 창의력 검사 프로그램")

if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.answers = {}
    st.session_state.gpt_scores = {}
    st.session_state.area_keys = list(questions.keys())

area_index = st.session_state.step // 5
question_index = st.session_state.step % 5

if area_index < len(st.session_state.area_keys):
    area = st.session_state.area_keys[area_index]
    question = questions[area][question_index]

    st.markdown(f"### {area} 영역 - 문항 {question_index + 1}/5")
    st.write(question)

    answer = st.text_area("답변을 입력하세요", key=f"{area}_{question_index}")

    if st.button("다음"):
        if area not in st.session_state.answers:
            st.session_state.answers[area] = []
            st.session_state.gpt_scores[area] = []

        st.session_state.answers[area].append(answer)
        gpt_result = gpt_score(question, answer)
        st.session_state.gpt_scores[area].append(gpt_result)

        st.session_state.step += 1
        st.rerun()

else:
    st.header("✅ 검사 결과 (GPT 평가 기반)")
    data = []
    for area in st.session_state.answers:
        for i, ans in enumerate(st.session_state.answers[area]):
            data.append({
                "영역": area,
                "문항 번호": i+1,
                "답변": ans,
                "GPT 평가": st.session_state.gpt_scores[area][i]
            })
    df = pd.DataFrame(data)

    for row in data:
        st.subheader(f"{row['영역']} - 문항 {row['문항 번호']}")
        st.markdown(f"**답변:** {row['답변']}")
        st.markdown(f"**GPT 평가:**\n{row['GPT 평가']}")

    st.download_button(
        label="📥 GPT 평가 포함 결과 다운로드",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name="GPT_창의력검사_결과.csv",
        mime="text/csv"
    )
