# app.py

import streamlit as st

from safety import (
    is_medical_question,
    safety_response
)

from rag import answer_question


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VinCare Hospital Assistant",
    page_icon="🏥",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #8b949e;
        margin-bottom: 25px;
    }

    .welcome-box {
        padding: 22px;
        border-radius: 12px;
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🏥 VinCare")

    st.caption(
        "Hospital Information Assistant"
    )

    st.divider()

    st.markdown("### 📋 Hospital Information")

    st.write(
        "Hospital details, timings and location."
    )

    st.markdown("### 👨‍⚕️ Doctors")

    st.write(
        "Doctors, specializations, rooms and schedules."
    )

    st.markdown("### 🏢 Departments")

    st.write(
        "Explore available hospital departments."
    )

    st.markdown("### 📞 Contacts")

    st.write(
        "Emergency, appointments, pharmacy and billing."
    )

    st.markdown("### 📜 Policies")

    st.write(
        "Hospital policies and patient information."
    )

    st.divider()

    st.caption(
        "Powered by RAG + Gemini"
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🏥 VinCare Hospital Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Your assistant for VinCare Hospital information.
    Ask about doctors, departments, schedules, contacts and policies.
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# WELCOME
# =========================================================

st.markdown(
    """
    <div class="welcome-box">

    <h3>👋 Welcome!</h3>

    <p>
    I can help you find information about VinCare Hospital.
    </p>

    <p>
    Try asking:
    </p>

    <ul>
        <li>What departments are available?</li>
        <li>Who are the cardiologists?</li>
        <li>What is Dr. Arjun Mehta's schedule?</li>
        <li>What is the emergency phone number?</li>
        <li>What are the appointment timings?</li>
    </ul>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SAFETY NOTICE
# =========================================================

st.info(
    "🛡️ This assistant provides hospital information only. "
    "It does not provide diagnosis, prescriptions, treatment "
    "recommendations or medical-test interpretation."
)


# =========================================================
# RESET BUTTON
# =========================================================

if st.button(
    "🔄 New Search",
    use_container_width=False
):

    st.session_state.pop(
        "current_question",
        None
    )

    st.session_state.pop(
        "current_answer",
        None
    )

    st.session_state.pop(
        "current_sources",
        None
    )

    st.rerun()


# =========================================================
# CURRENT SEARCH RESULT
# =========================================================

if "current_question" in st.session_state:

    st.markdown("### 🔎 Current Search")

    with st.chat_message("user"):

        st.markdown(
            st.session_state.current_question
        )

    with st.chat_message("assistant"):

        st.markdown(
            st.session_state.current_answer
        )

        sources = st.session_state.get(
            "current_sources",
            []
        )

        if sources:

            with st.expander(
                "📚 Sources"
            ):

                for source in sources:

                    st.caption(
                        f"• {source}"
                    )


# =========================================================
# SUGGESTED QUESTIONS
# =========================================================

st.markdown("### 💡 Try asking")

col1, col2, col3 = st.columns(3)


with col1:

    departments_clicked = st.button(
        "🏢 Departments",
        use_container_width=True
    )


with col2:

    doctors_clicked = st.button(
        "👨‍⚕️ Doctors",
        use_container_width=True
    )


with col3:

    emergency_clicked = st.button(
        "📞 Emergency Contact",
        use_container_width=True
    )


# =========================================================
# SUGGESTED QUESTION HANDLER
# =========================================================

selected_question = None

if departments_clicked:

    selected_question = (
        "List all departments available at VinCare Hospital."
    )

elif doctors_clicked:

    selected_question = (
        "List all doctors at VinCare Hospital."
    )

elif emergency_clicked:

    selected_question = (
        "What is the emergency phone number?"
    )


# =========================================================
# CHAT INPUT
# =========================================================

typed_question = st.chat_input(
    "Ask something about VinCare Hospital..."
)


if typed_question:

    selected_question = typed_question


# =========================================================
# PROCESS NEW SEARCH
# =========================================================

if selected_question:

    # -----------------------------------------------------
    # IMPORTANT:
    # Replace previous search completely
    # -----------------------------------------------------

    st.session_state.current_question = (
        selected_question
    )

    # Remove previous answer immediately

    st.session_state.pop(
        "current_answer",
        None
    )

    st.session_state.pop(
        "current_sources",
        None
    )


    # -----------------------------------------------------
    # Safety check
    # -----------------------------------------------------

    with st.spinner(
        "🔎 Searching hospital information..."
    ):

        if is_medical_question(
            selected_question
        ):

            answer = safety_response()

            sources = []

        else:

            answer, sources = answer_question(
                selected_question
            )


    # -----------------------------------------------------
    # Store ONLY current result
    # -----------------------------------------------------

    st.session_state.current_answer = answer

    st.session_state.current_sources = sources


    # -----------------------------------------------------
    # Rerun to display clean result
    # -----------------------------------------------------

    st.rerun()