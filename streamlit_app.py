import streamlit as st
import random
from openai import OpenAI

st.title("🎧 GPT와 함께하는 곡 디깅하기")

# 사용자 OpenAI 키 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("OpenAI API 키를 입력해주세요.", icon="🗝️")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# 세션 상태 초기화
for key in ["fav_songs", "concepts", "current_recs", "start_recommend"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key != "start_recommend" else False

# 1. 좋아하는 노래 입력
st.header("1. 좋아하는 노래를 입력해주세요.")
st.caption("최소 2곡, 최대 3곡 입력 가능")
st.caption("서로 다른 아티스트를 입력하면 더 정확한 추천 가능")

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
for i in range(1, 4):
    song = song_input(i)
    if song:
        fav_list.append(song)

if len(fav_list) < 2:
    st.warning("최소 2곡을 입력해야 추천을 시작할 수 있어요.")
    st.stop()
else:
    st.session_state.fav_songs = fav_list

# 2. 컨셉 선택
st.header("2. 원하는 노래 컨셉을 선택해주세요")
all_concepts = [
    "잔잔한", "신나는", "감성적인", "댄스", "락", "재즈", "힙합",
    "발라드", "클래식", "팝", "R&B", "일렉트로닉", "어쿠스틱", 
    "트로피컬", "인디", "포크", "블루스", "레게", "메탈"
]
selected_concepts = st.multiselect(
    "컨셉은 여러 개 선택 가능", all_concepts, key="multiselect_concept"
)
if selected_concepts:
    st.session_state.concepts = selected_concepts
else:
    st.warning("하나 이상의 컨셉을 선택해주세요.")

# 3. 개인 조건 입력
st.header("3. 추가 조건 (선택)")
additional_info = st.text_area(
    "원하는 조건을 적어주세요. 예: '국내 노래 위주', '2020~2023년 사이 발매' 등",
    placeholder="국내/해외, 발매 기간, 장르 등 자유롭게 작성"
)

# 🚀 추천 시작 버튼
if st.button("🚀 추천 시작하기"):
    if selected_concepts:
        st.session_state.start_recommend = True
    else:
        st.warning("컨셉을 먼저 선택해주세요!")

# 추천 단계
if st.session_state.start_recommend:
    st.header("4. 추천 노래 보기")

    def get_recommendations():
        concept = random.choice(st.session_state.concepts)
        fav_songs_str = ', '.join([f"{s['title']} - {s['artist']}" for s in st.session_state.get("fav_songs", [])])

        prompt = f"""
당신은 음악 큐레이터 역할을 맡고 있습니다. 
사용자가 입력한 정보를 기반으로 맞춤형 노래를 추천해주세요.

[사용자 입력 정보]
- 좋아하는 노래: {fav_songs_str}
- 원하는 분위기(컨셉): {concept}
- 추가 조건: {additional_info}

[추천 지침]
1. 위 정보를 바탕으로 분위기와 어울리는 노래 5곡을 추천해주세요.
2. 각 곡마다 추천 이유를 간단하지만 설득력 있게 설명해주세요.
3. 설명은 따뜻하고 친근한 톤으로 작성해주세요.

[출력 형식 예시]
"노래 제목 - 아티스트"를 추천드려요. 사용자님께서 ~~~ 를 원하셔서, 제가 ~~한 곡을 떠올려봤어요. 이 노래는 ~~ 이 돋보이는 곡입니다.

[주의 사항]
- 반드시 5곡을 추천해주세요.
- 같은 아티스트를 여러 번 추천하지 말아주세요.
- 사용자가 입력한 아티스트는 추천하지 말아주세요.
- 한국/해외 곡을 섞어서 추천해주세요.
"""

        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "user", "content": prompt}]
        )
        rec_text = response.choices[0].message.content.strip()
        return [line for line in rec_text.split("\n") if line.strip()]

    # 🎶 새로운 5곡 추천 버튼
    if st.button("🎶 새로운 5곡 추천받기"):
        st.session_state.current_recs = get_recommendations()

    # 추천곡 보여주기
    if st.session_state.current_recs:
        st.write("👉 추천드리는 노래 5곡:")
        for i, rec in enumerate(st.session_state.current_recs, start=1):
            st.write(f"{i}. {rec}")