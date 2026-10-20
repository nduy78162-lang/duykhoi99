
import streamlit as st
import random

st.set_page_config(page_title="Thử Thách Trí Tuệ", page_icon="🧠")

st.title("🧠 THỬ THÁCH TRÍ TUỆ")
st.write("Trả lời câu hỏi và kiểm tra khả năng tư duy của bạn!")

questions = [
    {
        "q": "Số tiếp theo là gì: 2, 4, 8, 16, ...?",
        "options": ["18", "24", "32", "36"],
        "answer": "32"
    },
    {
        "q": "Một tuần có bao nhiêu ngày?",
        "options": ["5", "6", "7", "8"],
        "answer": "7"
    },
    {
        "q": "Số nào là số nguyên tố?",
        "options": ["9", "15", "17", "21"],
        "answer": "17"
    },
    {
        "q": "Nếu hôm nay là thứ Hai, 3 ngày nữa là thứ mấy?",
        "options": ["Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu"],
        "answer": "Thứ Năm"
    },
    {
        "q": "12 × 8 bằng bao nhiêu?",
        "options": ["86", "96", "108", "88"],
        "answer": "96"
    }
]

if "questions" not in st.session_state:
    st.session_state.questions = random.sample(questions, len(questions))
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.done = False

if not st.session_state.done:
    i = st.session_state.index
    question = st.session_state.questions[i]

    st.progress(i / len(questions))
    st.subheader(f"Câu {i + 1}: {question['q']}")

    choice = st.radio(
        "Chọn đáp án:",
        question["options"],
        key=f"answer_{i}"
    )

    if st.button("Xác nhận đáp án"):
        if choice == question["answer"]:
            st.session_state.score += 1
            st.success("Chính xác! 🎉")
        else:
            st.info(f"Đáp án đúng là: {question['answer']}")

        if i + 1 == len(questions):
            st.session_state.done = True
        else:
            st.session_state.index += 1

        st.rerun()
else:
    st.balloons()
    st.header("🎉 Bạn đã hoàn thành!")
    st.metric("Điểm số", f"{st.session_state.score}/{len(questions)}")

    if st.button("Chơi lại"):
        for key in ["questions", "index", "score", "done"]:
            del st.session_state[key]
        st.rerun()

