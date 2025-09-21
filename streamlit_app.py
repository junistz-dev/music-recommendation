import streamlit as st
from openai import OpenAI
import random

st.title("🎧 GPT와 함께하는 곡 디깅하기")
# 사용자에게 OpenAI 키 입력 받기
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("OpenAI API 키를 입력해주세요.", icon="🗝️")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 세션 상태 초기화
if "fav_songs" not in st.session_state:
    st.session_state.fav_songs = []
if "concepts" not in st.session_state:
    st.session_state.concepts = []
if "current_recs" not in st.session_state:
    st.session_state.current_recs = []
if "rec_index" not in st.session_state:
    st.session_state.rec_index = 0
if "finished" not in st.session_state:   # ← 여기 추가
    st.session_state.finished = False

# 1. 좋아하는 노래 입력
st.header("1. 좋아하는 노래를 입력해주세요. ")
st.caption("최소 2곡을 적어주셔야 해요, 최대 3곡까지 입력 가능!")
st.caption("서로 다른 아티스트를 적으면 더 좋은 추천이 가능해요.")

def song_input(idx):
    col1, col2 = st.columns([2, 2])
    with col1:
        title = st.text_input(f"노래 {idx} 제목", key=f"title_{idx}")
    with col2:
        artist = st.text_input(f"노래 {idx} 아티스트", key=f"artist_{idx}")
    if title.strip() and artist.strip():
        return {"title": title.strip(), "artist": artist.strip()}
    return None

fav_list = []
for i in range(1, 4):  # 3곡까지 입력 가능
    song = song_input(i)
    if song:
        fav_list.append(song)

if len(fav_list) < 2:
    st.warning("최소 2곡(제목 + 아티스트)을 입력하셔야 추천을 시작할 수 있어요.")
    st.stop()
else:
    st.session_state.fav_songs = fav_list

# 2. 컨셉 선택 (여러 개 선택 가능)
st.header("2. 원하는 노래 컨셉을 선택해주세요")
all_concepts = [
    "잔잔한", "신나는", "감성적인", "댄스", "락", "재즈", "힙합",
    "발라드", "클래식", "팝", "R&B", "일렉트로닉", "어쿠스틱", 
    "트로피컬", "인디", "포크", "블루스", "레게", "메탈"
]
selected_concepts = st.multiselect(
    "컨셉은 여러 개 선택이 가능해요.", 
    all_concepts, 
    key="multiselect_concept"
)

if not selected_concepts:
    st.warning("하나 이상의 컨셉을 선택해주세요.")
    st.stop()
else:
    st.session_state.concepts = selected_concepts

# 3. 추천 단계
st.header("3. 추천 노래 보기")

if not st.session_state.finished:
    if not st.session_state.current_recs:
        concept = random.choice(st.session_state.concepts)
        # fav_songs를 문자열로 변환
        fav_songs_str = ', '.join([f"{s['title']} - {s['artist']}" for s in st.session_state.fav_songs])
        
        prompt = f"""
        사용자가 좋아하는 노래: {fav_songs_str}
        원하는 분위기(컨셉): {concept}

        위 조건에 맞는 노래 5곡을 추천하고, 각 곡마다 추천 이유를 간단히 설명해주세요.
        출력 형식은 아래와 같이 해주세요:
        "노래 제목 - 아티스트"를 추천드려요. 사용자님께서 원하는 분위기에 맞춰서 ~~면 좋다고 생각해봤어요. 이 노래는 ~한 노래입니다. 어떠신가요?
        """
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": prompt}]
        )
        rec_text = response.choices[0].message.content.strip()
        st.session_state.current_recs = [line for line in rec_text.split("\n") if line.strip()]
        st.session_state.rec_index = 0

    if st.session_state.rec_index < len(st.session_state.current_recs):
        recommendation = st.session_state.current_recs[st.session_state.rec_index]
        st.write(f"👉 추천 노래: **{recommendation}**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("이 노래 알아요"):
                st.session_state.rec_index += 1  # 다음 곡으로 이동
        with col2:
            if st.button("좋아요, 이걸로 끝내요"):
                st.session_state.finished = True

    # 추천 곡이 모두 끝났거나 종료 버튼 클릭 시
    if st.session_state.finished:
        st.success("추천을 종료할게요! 즐거운 노래 감상 되세요 🎶")
    elif st.session_state.rec_index >= len(st.session_state.current_recs):
        st.success("선택된 컨셉에서 추천 가능한 곡을 모두 보여드렸습니다!")
        st.session_state.finished = True
        ## need to end, ㅂ