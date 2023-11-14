import streamlit as st
import sqlite3

# 데이터베이스 연결을 열기 위한 함수
def get_connection():
    conn = sqlite3.connect('./guest.db', check_same_thread=False)
    return conn


# 상태를 초기화하는 함수
def initialize_state():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "input_content" not in st.session_state:
        st.session_state.input_content = ""


# Streamlit 앱 초기화
initialize_state()
conn = get_connection()

# 로그인 페이지
if st.session_state.page == "login":
    st.title("회원가입과 로그인을 해보세요!")
    st.header("로그인")
    if not st.session_state.logged_in:
        login_id = st.text_input("사용자 이름:")
        login_pw = st.text_input("비밀번호:", type="password")

        login_button = st.button("로그인")

        if login_button:
            cursor = conn.cursor()
            cursor.execute("SELECT id, pw FROM user WHERE id = ? AND pw = ?", (login_id, login_pw))
            user = cursor.fetchone()

            if user:
                st.success("로그인되었습니다. 로그인 버튼을 다시 눌러 위 창을 없앨 수 있습니다.")
                st.session_state.logged_in = True
                st.session_state.page = "home"
                st.session_state.username = login_id
            else:
                st.error("사용자 이름 또는 비밀번호가 올바르지 않습니다.")

# 홈 페이지
if st.session_state.page == "home":
    st.title("방명록을 남겨보세요!")
    st.header(f"환영합니다, {st.session_state.username}! 로그인이 완료되었습니다.")
    st.write("입력 또는 like/dislike 버튼을 누른 뒤 클릭해주세요")
    # 로그아웃
    if st.button("갱신"):
        initialize_state()
    # 데이터베이스에서 콘텐츠를 가져오고 업데이트
    cursor = conn.cursor()
    cursor.execute("SELECT num, text, good, dislike FROM msg")
    text = cursor.fetchall()

    # 데이터베이스에 콘텐츠 삽입
    input_content = st.text_input("원하는 내용을 입력하세요:", key="input_content")
    if st.button("입력"):
        if input_content:
            cursor.execute("INSERT INTO msg (text, good, dislike) VALUES (?, 0, 0)", (input_content,))
            conn.commit()
            conn = get_connection()  # 데이터베이스 연결 열기
            initialize_state()

    # 콘텐츠를 표시하고 좋아요/싫어요를 허용
    st.subheader("방명록:")
    for row in text:
        st.write(f"번호: {row[0]}, 내용: {row[1]}")
        st.write(f"like: {row[2]}, dislike: {row[3]}")
        like_button_key = f'like_button_{row[0]}'
        dislike_button_key = f'dislike_button_{row[0]}'

        if st.button('like', key=like_button_key):
            cursor.execute("UPDATE msg SET good = good + 1 WHERE num = ?", (row[0],))
            conn.commit()
            initialize_state()
        if st.button('dislike', key=dislike_button_key):
            cursor.execute("UPDATE msg SET dislike = dislike + 1 WHERE num = ?", (row[0],))
            conn.commit()
            initialize_state()

# 회원가입 페이지
if not st.session_state.logged_in:
    st.header("회원가입")
    signup_id = st.text_input("사용자 이름:", key="signup_id")
    signup_pw = st.text_input("비밀번호:", type="password", key="signup_pw")
    signup = st.button("가입")

    if signup:
        conn = get_connection()  # 데이터베이스 연결 열기
        cursor = conn.cursor()

        # 가입 버튼을 클릭한 경우 아이디 중복 확인
        cursor.execute("SELECT id FROM user WHERE id = ?", (signup_id,))
        existing_user = cursor.fetchone()
        if existing_user:
            st.error("이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
        else:
            # 가입 로직을 처리하고 데이터베이스에 추가
            cursor.execute("INSERT INTO user (id, pw) VALUES (?, ?)", (signup_id, str(signup_pw)))
            conn.commit()  # 변경사항을 저장
            conn.close()  # 데이터베이스 연결 닫기
            st.success("회원가입이 완료되었습니다.")
