import streamlit as st
from transformers import pipeline
qa_pipeline = pipeline("question-answering", model="distilbert/distilbert-base-cased-distilled-squad")
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from difflib import get_close_matches
from openai import OpenAI

# Show title and description.
st.title("💬 FAQ for Yonsei International Summer School")
st.write(
    "👋 Welcome to the YISS Chatbot!"
    "Feel free to ask me anything."
)

# Google Sheets API 인증 및 데이터 로드 함수
def load_qa_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("yiss-3535-2f95e38683f7.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("YISS_FAQ").sheet1  # 스프레드시트 이름으로 불러옴
    qa_data = pd.DataFrame(sheet.get_all_records())
    return qa_data['Question'].tolist(), qa_data['Answer'].tolist()

# Hugging Face의 QA 모델 로드
qa_pipeline = pipeline("question-answering")

# 초기 데이터 로드
questions, answers = load_qa_data()

def find_best_answer(user_input):
    # 가장 유사한 질문 찾기
    matches = get_close_matches(user_input, questions, n=1, cutoff=0.5)
    if matches:
        best_match = matches[0]
        answer_index = questions.index(best_match)
        return f"{answers[answer_index]} 🦅 I hope the information provided was helpful for you! Feel free to let us know if you need further assistance."
    else:
        return "I'm sorry I couldn't fully address your question here. Please email us to summer@yonsei.ac.kr with more details so we can assist further. We'll do our best to improve, so that we can assist you better in the future! 🦅"

# Streamlit 앱 설정
st.title("FAQ for Yonsei International Summer School")
st.write("👋 Welcome to the YISS Chatbot! Feel free to ask me anything.")

# 세션 상태를 사용하여 질문과 답변 리스트 저장
if 'qa_pairs' not in st.session_state:
    st.session_state.qa_pairs = []

# 새로고침 버튼
if st.button("Refresh Data"):
    questions, answers = load_qa_data()
    st.write("The Q&A data has been updated!")

# 이전 질문 삭제 버튼
if st.button("Delete Previous Questions"):  # 버튼 제목
    st.session_state.qa_pairs = []  # 질문과 답변 리스트 초기화
    st.write("Previous questions have been cleared!")  # 확인 메시지

# 질문 입력
user_input = st.text_input("Ask me anything:")
if st.button("Ask"):
    if user_input:  # 사용자가 질문을 입력했는지 확인
        answer = find_best_answer(user_input)
        st.session_state.qa_pairs.append((user_input, answer))  # 질문과 답변 저장
    else:
        st.warning("Please enter a question before clicking 'Ask'.")  # 질문 입력 안내

# 이전 질문과 답변 표시
if st.session_state.qa_pairs:
    st.write("### Previous Questions and Answers:")
    for q, a in st.session_state.qa_pairs:
        st.write(f"**Q:** {q}")
        st.write(f"**A:** {a}")
