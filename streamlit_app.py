# 창의력 검사 프로그램

import ipywidgets as widgets
from IPython.display import display, clear_output, FileLink
import pandas as pd
from tqdm.notebook import tqdm
import re

# 스타일 설정
style = {'description_width': 'initial'}
layout = widgets.Layout(width='80%', height='200px')

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

# 점수 계산 함수

def count_ideas(answer):
    ideas = re.split(r'[\,\n]+', answer.strip())
    return len([idea for idea in ideas if idea.strip()])

def originality_score(answer):
    words = re.findall(r'\b\w{6,}\b', answer.lower())
    return len(set(words))

def elaboration_score(answer):
    return min(len(answer.strip()) // 20, 5)

def calculate_score(area_name, answer):
    if area_name == "유창성":
        return count_ideas(answer)
    elif area_name == "독창성":
        return originality_score(answer)
    elif area_name == "정교성":
        return elaboration_score(answer)
    elif area_name == "융통성":
        return count_ideas(answer)
    elif area_name == "상상력":
        return elaboration_score(answer) + originality_score(answer)
    return 0

# 창의력 검사 클래스
class CreativityTest:
    def __init__(self):
        self.current_area = 0
        self.current_question = 0
        self.answers = {}
        self.scores = {}

        self.progress = widgets.IntProgress(value=0, max=25, description='진행률:')
        self.question_label = widgets.HTML()
        self.answer_text = widgets.Textarea(layout=layout, style=style)
        self.next_button = widgets.Button(description='다음', button_style='primary')
        self.score_display = widgets.HTML()
        self.export_button = widgets.Button(description='결과 엑셀 저장', button_style='success')

        self.next_button.on_click(self.next_question)
        self.export_button.on_click(self.export_results)
        self.update_display()

    def update_display(self):
        clear_output(wait=True)
        display(self.progress)

        if self.current_area < len(questions):
            area_name = list(questions.keys())[self.current_area]
            question = questions[area_name][self.current_question]

            card_html = f"""
            <div style='border: 2px solid #ccc; padding: 20px; margin: 10px 0; border-radius: 10px;'>
                <h3>{area_name} 영역 - 문항 {self.current_question + 1}/5</h3>
                <p>{question}</p>
            </div>
            """
            self.question_label.value = card_html
            display(self.question_label)
            display(self.answer_text)
            display(self.next_button)
        else:
            self.show_results()

    def next_question(self, b):
        area_name = list(questions.keys())[self.current_area]

        if area_name not in self.answers:
            self.answers[area_name] = []
        self.answers[area_name].append(self.answer_text.value)

        score = calculate_score(area_name, self.answer_text.value)
        if area_name not in self.scores:
            self.scores[area_name] = 0
        self.scores[area_name] += score

        self.current_question += 1
        if self.current_question >= 5:
            self.current_area += 1
            self.current_question = 0

        self.progress.value = self.current_area * 5 + self.current_question
        self.answer_text.value = ''
        self.update_display()

    def show_results(self):
        results_html = "<h2>검사 결과</h2>"
        total_score = 0

        for area, score in self.scores.items():
            results_html += f"<h3>{area}: {score}점</h3>"
            total_score += score

        results_html += f"<h2>총점: {total_score}점</h2>"
        self.score_display.value = results_html
        display(self.score_display)
        display(self.export_button)

    def export_results(self, b):
        data = []
        for area in self.answers:
            for i, answer in enumerate(self.answers[area]):
                data.append({
                    '영역': area,
                    '문항 번호': i + 1,
                    '답변': answer,
                    '점수': calculate_score(area, answer)
                })

        df = pd.DataFrame(data)
        df.to_excel("창의력검사_결과.xlsx", index=False)
        display(FileLink("창의력검사_결과.xlsx"))

# 창의력 검사 시작
test = CreativityTest()
