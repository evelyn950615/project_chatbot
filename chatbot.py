import streamlit as st
import openai
import os
from dotenv import load_dotenv
import gpts_prompt

def gpt_feedback_to_html(gpt_feedback):
    html = gpt_feedback
    html = html.replace("[강점]", "<span style='color:#2563eb; font-weight:bold;'>📈 강점</span>")
    html = html.replace("[약점]", "<span style='color:#ef4444; font-weight:bold;'>⚠️ 약점</span>")
    html = html.replace("[추천 역할]", "<span style='color:#06b6d4; font-weight:bold;'>🎯 추천 역할</span>")
    html = html.replace("[성장 조언]", "<span style='color:#f59e42; font-weight:bold;'>🚀 성장 조언</span>")
    html = html.replace("[응원 메시지]", "<span style='color:#6366F1; font-weight:bold;'>💬 응원 메시지</span>")
    html = html.replace("\n\n", "</p><p>")
    html = html.replace("\n", "<br>")
    return "<p>" + html + "</p>"

# --- 환경설정 ---
st.set_page_config(page_title="팀 페르소나 진단 챗봇", layout="centered")
st.markdown(
    """
    <style>
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: bold;
        border: none;
        transition: background 0.2s;
        outline: none;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: #fff !important;
    }
    .stButton>button:focus {
        outline: 2.5px solid #6366F1;
        outline-offset: 2px;
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("🧩 팀 페르소나 진단 챗봇")

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
system_prompt = gpts_prompt.SYSTEM_PROMPT

# --- 진단 질문 ---
questions = [
    {
        "q": "Q1. 팀 프로젝트가 시작되면, 나는 가장 먼저 무엇을 하나요?",
        "options": [
            "전체 전략/계획을 짠다. (기획자형)",
            "바로 실행, 실무를 맡는다. (실행가형)",
            "사람/자원 연결, 네트워킹을 한다. (네트워크형)",
            "데이터/정보를 분석해 의견을 낸다. (분석가형)",
            "전체 방향, 미래 비전을 상상한다. (비전리더형)"
        ]
    },
    {
        "q": "Q2. 팀 내 갈등이 생기면, 나는?",
        "options": [
            "구조적으로 문제를 정리, 대안을 찾는다. (기획자형)",
            "행동으로 먼저 나서서 해결한다. (실행가형)",
            "모두가 말할 수 있게 분위기를 만든다. (네트워크형)",
            "논리적 근거, 데이터를 들어 설득한다. (분석가형)",
            "장기적 관점, 전체 방향성을 점검한다. (비전리더형)"
        ]
    },
    {
        "q": "Q3. 팀 회의에서 나는 주로…",
        "options": [
            "주제를 리드, 플랜을 제안한다. (기획자형)",
            "실행 가능한 액션을 빠르게 정리한다. (실행가형)",
            "팀원 의견을 잘 이끌어낸다. (네트워크형)",
            "수치·자료로 설득한다. (분석가형)",
            "다양한 의견을 모아 큰 그림을 그린다. (비전리더형)"
        ]
    },
    {
        "q": "Q4. 내가 팀에서 가장 자신 있는 강점은?",
        "options": [
            "전략/기획 (기획자형)",
            "실행력 (실행가형)",
            "팀워크/커뮤니케이션 (네트워크형)",
            "분석/문제해결 (분석가형)",
            "창의적 비전 (비전리더형)"
        ]
    },
    {
        "q": "Q5. 새로운 도전 앞에서 나는…",
        "options": [
            "전체 계획을 세운다. (기획자형)",
            "빠르게 실험/실행한다. (실행가형)",
            "파트너, 네트워크를 먼저 찾는다. (네트워크형)",
            "자료/사례 분석부터 한다. (분석가형)",
            "미래 성공 모습을 상상한다. (비전리더형)"
        ]
    }
]

# --- 세션 상태 관리 ---
if "step" not in st.session_state:
    st.session_state["step"] = 0   # 인트로부터 시작!
if "answers" not in st.session_state:
    st.session_state["answers"] = []
if "result" not in st.session_state:
    st.session_state["result"] = None

step = st.session_state["step"]
answers = st.session_state["answers"]

def reset_all():
    st.session_state.clear()          # 세션 상태 전체 초기화
    st.session_state["step"] = 0      # 진단 인트로로 초기화
    st.session_state["answers"] = []  # 답변 리스트 초기화
    st.session_state["result"] = None

st.markdown("---")

# --- 인트로(진단 시작) ---
if st.session_state["step"] == 0:
    st.markdown("""
        <div style='background:#eef6ff; border-radius:16px; padding:30px 22px 20px 22px; margin-bottom:20px'>
            <h2 style="color:#2563eb; margin-bottom:6px;">
                TeamCanvas 팀 페르소나 진단 챗봇에 오신 걸 환영합니다!
            </h2>
            <div style="font-size:1.14rem; margin-bottom:8px;">
                <span style="color:#222;">
                <b>TeamCanvas</b>는 팀 프로젝트 또는 협업 환경에서<br>
                당신이 가장 잘 발휘할 수 있는 <b>역할/강점/팀 내 페르소나</b>를<br>
                <b>5가지 핵심 질문</b>을 통해 빠르게 진단해주는 AI 도구입니다.<br><br>
                결과 리포트에서는 추천 역할, 실무 팁, 성장 포인트까지 확인할 수 있습니다.
                </span>
            </div>
            <div style="font-weight:bold; color:#2563eb;">
                아래 버튼을 눌러 진단을 시작하세요.
            </div>
        </div>
        """, unsafe_allow_html=True)
    if st.button("진단 시작하기 🚀"):
        st.session_state["step"] = 1

# --- 단계별 질문 진행 ---
elif step <= len(questions):
    q = questions[step-1]
    st.markdown(f'<div class="question-card"><h4 style="color:#2563eb;">{q["q"]}</h4>', unsafe_allow_html=True)
    option = st.radio(
        "가장 적합한 답을 선택하세요.",
        q["options"],
        key=f"q_{step}"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("다음", key=f"next_{step}"):
        answers.append(option)
        st.session_state["answers"] = answers
        st.session_state["step"] += 1

# --- 결과 카드/분석 ---
else:
    from collections import Counter
    labels = ["기획자형", "실행가형", "네트워크형", "분석가형", "비전리더형"]
    count = Counter()
    for ans in answers:
        for l in labels:
            if l in ans:
                count[l] += 1
    if count:
        top_type, top_score = count.most_common(1)[0]
        # 결과 설명 딕셔너리
        type_desc = {
            "기획자형": "전체 그림을 그리고 전략과 플랜을 설계하는 타입입니다.",
            "실행가형": "즉각적으로 행동하며 팀을 추진하는 실행력의 소유자입니다.",
            "네트워크형": "사람·자원 네트워킹, 팀 소통, 조율이 강점입니다.",
            "분석가형": "데이터와 근거로 문제를 해결하고 논리적 설득을 잘합니다.",
            "비전리더형": "미래 트렌드, 창의적 비전 제시, 큰 그림을 잘 그립니다."
        }
        # 미적으로 결과카드 꾸미기
        st.markdown(
            f"""
            <div style="background:linear-gradient(90deg,#3B82F6 60%,#6366F1 100%);
                        color:white; border-radius:16px; padding:30px 30px 18px 30px;
                        margin:10px 0 20px 0; box-shadow:0 4px 18px rgba(59,130,246,0.09)">
            <h2 style="font-size:2.3rem; margin-bottom:10px;">🎉 당신은 <b>{top_type}</b>입니다!</h2>
            <p style="font-size:1.3rem; line-height:1.6;">
                {type_desc[top_type]}
            </p>
            </div>
            """, unsafe_allow_html=True)

        # --- [여기에 GPT 피드백 생성 블록 추가!] ---
        import time
        with st.spinner("GPT가 맞춤 피드백을 생성 중입니다..."):
            user_type = top_type
            user_answers = "\n".join(f"{i+1}. {a}" for i, a in enumerate(answers))
            gpt_prompt = f"""
            아래는 팀 페르소나 진단 테스트 결과입니다.
            - 사용자의 주요 유형: {user_type}
            - 각 질문별 답변: 
            {user_answers}

            이 정보를 바탕으로,
            1) 해당 유형의 대표 강점/약점,
            2) 추천 직무 또는 팀 내 역할,
            3) 실무/성장 조언, 
            4) 추가 응원 메시지 
            를 각각 2~3줄 이내로 핵심만 한국어로 써줘.
            불필요한 인삿말/마무리 문장 없이, 각 항목별로 [강점], [약점], [추천 역할], [성장 조언], [응원 메시지] 식으로 정리해.
            """

            client = openai.OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": gpt_prompt},
                ],
                temperature=0.5,
            )
            gpt_feedback = response.choices[0].message.content.strip()
            time.sleep(0.6)


            gpt_feedback_html = gpt_feedback_to_html(gpt_feedback)   # <--- 추가!

        st.markdown(
            f"""
            <div style="background:#f8fafc; border-radius:15px; padding:18px 22px 12px 22px; margin-top:18px; border:1px solid #dbeafe">
                <h4 style="color:#6366F1;">📝 GPT가 분석한 나의 맞춤 피드백</h4>
                <div style="font-size:1.12rem; color:#222; line-height:1.85; margin-top:6px; white-space:pre-wrap">{gpt_feedback_html}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
    else:
        st.warning("진단 결과를 볼 수 없습니다. 모든 질문에 답변해 주세요.")

    if st.button("🔄 처음부터 다시하기"):
        reset_all()
        st.rerun()
