import sys
from pathlib import Path
import pandas as pd

import streamlit as st


#====================================
# PATH SETUP
#====================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


#========================================================
# IMPORTS
#========================================================

from ingest import ingest_pdf
from rag import generate_answer
from summarizer import summarize_document
from vector_store import list_documents
from quiz import generate_quiz
from progress import (
    save_quiz_result,
    load_progress,
    get_statistics
)


#========================================================
# PAGE CONFIG
#========================================================
st.set_page_config(
    page_title="StudyBuddy",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

#========================================================
# CUSTOM STYLING
#========================================================
st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        opacity: 0.75;
        margin-top: 0;
    }

    .feature-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 15px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 650;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0

if "quiz_percentage" not in st.session_state:
    st.session_state.quiz_percentage = 0.0

if "generated_quiz_document" not in st.session_state:
    st.session_state.generated_quiz_document = None

if "quiz_id" not in st.session_state:
    st.session_state.quiz_id = 0

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 📚 StudyBuddy")

    st.caption(
        "AI-Powered Personalized Learning Assistant"
    )

    st.markdown("---")

    st.markdown("### 🧭 Navigation")

    st.info(
        "Use the tabs above to move between "
        "learning tools."
    )

    st.markdown("---")

    st.markdown("### 📄 Study Materials")

    try:
        sidebar_documents = list_documents()

        if sidebar_documents:

            st.metric(
                "Indexed Documents",
                len(sidebar_documents)
            )

            for document in sidebar_documents:
                st.caption(f"📄 {document}")

        else:

            st.caption(
                "No documents indexed yet."
            )

    except Exception as error:

        st.caption(
            f"Unable to load documents: {error}"
        )

    st.markdown("---")

    st.markdown("### 🤖 AI Model")

    st.caption("Qwen 2.5 — 1.5B")

    st.caption("Embeddings: nomic-embed-text")

    st.markdown("---")

    st.caption(
        "StudyBuddy • Local AI Learning Assistant"
    )

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📚 StudyBuddy</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Personalized Learning Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Turn your study material into an interactive "
    "learning experience."
)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
        <div class="feature-card">
        <h3>💬 Ask</h3>
        <p>Ask questions directly from your study material.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
        <h3>📝 Summarize</h3>
        <p>Generate concise revision summaries.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
        <h3>🧠 Quiz</h3>
        <p>Generate AI-powered MCQ quizzes.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <div class="feature-card">
        <h3>📊 Track</h3>
        <p>Monitor quiz scores and learning progress.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("📄 Study Materials")

uploaded_files = st.sidebar.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# ============================================================
# PDF UPLOAD
# ============================================================

if uploaded_files:

    documents_dir = (
        PROJECT_ROOT / "data" / "documents"
    )

    documents_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for uploaded_file in uploaded_files:

        file_path = (
            documents_dir / uploaded_file.name
        )

        if not file_path.exists():

            with open(
                file_path,
                "wb"
            ) as file:

                file.write(
                    uploaded_file.getbuffer()
                )

            st.sidebar.success(
                f"Uploaded: {uploaded_file.name}"
            )

            try:

                ingest_pdf(
                    str(file_path)
                )

                st.sidebar.success(
                    f"Indexed: {uploaded_file.name}"
                )

            except Exception as error:

                st.sidebar.error(
        "❌ Unable to process this PDF."
    )

                st.sidebar.info(
        "Please make sure the file is a valid PDF "
        "and try again."
    )

                with st.sidebar.expander("Technical details"):
                    st.code(str(error))

        else:

            st.sidebar.info(
                f"{uploaded_file.name} already exists."
            )


# ============================================================
# DOCUMENT LIST
# ============================================================

documents = list_documents()

if documents:

    st.sidebar.markdown("---")

    st.sidebar.subheader(
        "📚 Indexed Documents"
    )

    for document in documents:

        st.sidebar.write(
            f"📄 {document}"
        )


# ============================================================
# TABS
# ============================================================

tab_dashboard, tab_qa, tab_summary, tab_quiz, tab_progress = st.tabs(
    [
        "🏠 Dashboard",
        "💬 Ask",
        "📝 Summary",
        "🧠 Quiz",
        "📊 Progress"
    ]
)


# ============================================================
# TAB 1 — ASK AI
# ============================================================

with tab_qa:

    st.header("💬 Ask Questions")

    if not documents:

        st.info(
            "Upload a PDF to start asking questions."
        )

    else:

        qa_document = st.selectbox(
            "Select study material",
            documents,
            key="qa_document"
        )

        question = st.text_input(
            "Ask a question:",
            placeholder="Example: What is a DBMS?"
        )

        if st.button(
            "🤖 Ask AI",
            type="primary",
            key="ask_ai_button"
        ):

            if not question.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                with st.spinner(
                    "Searching study material..."
                ):

                    try:

                        answer, sources = generate_answer(
                            question,
                            n_results=3
                        )

                        st.markdown(
                            "### 🤖 Answer"
                        )

                        st.write(answer)

                        if sources:

                            st.markdown(
                                "### 📚 Sources"
                            )

                            for source in sources:

                                st.write(
                                    f"📄 {source['source']} "
                                    f"(Chunk {source['chunk_index']})"
                                )

                    except Exception as error:

                        st.error(
    "❌ Unable to generate an answer."
)

                        st.info(
    "Try asking a question related to "
    "your uploaded study material."
)

                        with st.expander("Technical details"):
                            st.code(str(error))


# ============================================================
# TAB 2 — SUMMARY
# ============================================================

with tab_summary:

    st.header("📝 AI Summary")

    if not documents:

        st.info(
            "Upload a PDF to generate a summary."
        )

    else:

        summary_document = st.selectbox(
            "Select document",
            documents,
            key="summary_document"
        )

        if st.button(
            "📝 Generate Summary",
            type="primary",
            key="summary_button"
        ):

            with st.spinner(
                "Generating summary..."
            ):

                try:

                    summary = summarize_document(
                        summary_document
                    )

                    st.markdown(summary)

                except Exception as error:

                    st.error(
    "❌ Summary generation failed."
)

                    st.info(
    "The local AI model may still be processing "
    "the document. Please try again."
)

                    with st.expander("Technical details"):
                        st.code(str(error))


# ============================================================
# TAB 3 — QUIZ
# ============================================================

with tab_quiz:

    st.header("🧠 AI Quiz Generator")

    st.write(
        "Generate multiple-choice questions using "
        "only your uploaded study material."
    )

    if not documents:

        st.info(
            "Upload a PDF to generate a quiz."
        )

    else:

        # IMPORTANT:
        # This key belongs ONLY to the selectbox.
        quiz_document_selector = st.selectbox(
            "📄 Select study material",
            documents,
            key="quiz_document_selector"
        )

        question_count = st.selectbox(
            "🔢 Number of questions",
            [5, 10, 15],
            index=0,
            key="quiz_question_count"
        )

        st.write("")
        

        if st.button(
            "🎯 Generate Quiz",
            type="primary",
            key="generate_quiz_button"
        ):

            # Clear old quiz
            if "quiz_id" not in st.session_state:
                st.session_state.quiz_id = 0
            st.session_state.quiz = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_score = 0
            st.session_state.quiz_percentage = 0.0
            st.session_state.quiz_id += 1

            with st.status(                             "🤖 Generating quiz...",
            expanded=True
            ) as status:

                st.write("📄 Reading indexed study material...")
                st.write("🧠 Asking Qwen to generate questions...")

                try:

                    quiz = generate_quiz(
                        source=quiz_document_selector,
                        number_of_questions=question_count
                    )
                    st.write(
    "DEBUG — quiz returned:",
    type(quiz).__name__,
    len(quiz) if isinstance(quiz, list) else "N/A"
)
                    st.write("✅ Quiz generated. Validating questions...")
# ==========================================
# FINAL QUIZ SAFETY VALIDATION
# ==========================================
        
                    if quiz is None:
                        raise ValueError(
        "Quiz generation returned no result."
    )

                    if not isinstance(quiz, list):
                        raise ValueError(
        f"Invalid quiz format: {type(quiz).__name__}"
    )

                    if len(quiz) == 0:
                        raise ValueError(
        "Quiz generation failed. Check the terminal for the "
        "actual generation/validation error."
    )

                    if not isinstance(quiz, list):
                        raise ValueError(
        "Invalid quiz format returned by AI."
    )

                    for index, question in enumerate(quiz, start=1):

                        required_fields = [
        "question",
        "options",
        "answer",
        "explanation"
    ]

                        for field in required_fields:

                            if field not in question:
                                raise ValueError(
                f"Question {index}: "
                f"Missing field '{field}'."
            )

                        if len(question["options"]) != 4:
                            raise ValueError(
            f"Question {index}: "
            "Expected exactly 4 options."
        )

                        answer = int(question["answer"])

                        if answer not in [1, 2, 3, 4]:
                            raise ValueError(
            f"Question {index}: "
            "Answer must be between 1 and 4."
        )

                    # Store generated quiz
                    st.session_state.quiz = quiz

                    # Store document separately
                    # from the selectbox widget
                    st.session_state.generated_quiz_document = (
                        quiz_document_selector
                    )
                    status.update(
    label="✅ Quiz generated successfully!",
    state="complete",
    expanded=False
)

                    st.session_state.quiz_submitted = False

                    st.success(
                        f"✅ Quiz generated successfully! "
                        f"{len(quiz)} questions ready."
                    )

                except Exception as error:

                    st.error(
                        "❌ Quiz generation failed."
                    )

                    st.exception(error)


    # ========================================================
    # DISPLAY QUIZ
    # ========================================================

    if st.session_state.quiz:

        quiz = st.session_state.quiz

        st.markdown("---")

        st.subheader(
            f"📋 Quiz — "
            f"{st.session_state.generated_quiz_document}"
        )

        answers = {}

        for index, question in enumerate(
            quiz
        ):

            st.markdown(
                f"### Question {index + 1}"
            )

            st.write(
                question["question"]
            )

            options = question["options"]

            answers[index] = st.radio(
                "Choose your answer:",
                options,
                key=f"quiz_answer_{st.session_state.quiz_id}_{index}",
                index=None
            )


        # ====================================================
        # SUBMIT
        # ====================================================

        st.markdown("")

        if st.button(
            "✅ Submit Quiz",
            type="primary",
            key="submit_quiz_button"
        ):

            score = 0

            for index, question in enumerate(
                quiz
            ):

                selected_answer = answers[index]

                correct_number = int(
                    question["answer"]
                )

                correct_answer = (
                    question["options"][
                        correct_number - 1
                    ]
                )

                if (
                    selected_answer
                    and
                    selected_answer == correct_answer
                ):

                    score += 1


            total_questions = len(quiz)

            percentage = (
                score / total_questions
            ) * 100


            st.session_state.quiz_score = score

            st.session_state.quiz_percentage = (
                percentage
            )

            st.session_state.quiz_submitted = True


            # Save progress
            try:

                save_quiz_result(
                    document=(
                        st.session_state
                        .generated_quiz_document
                    ),
                    score=score,
                    total=total_questions,
                    percentage=percentage
                )

            except Exception as error:

                st.warning(
                    f"Quiz completed, but progress "
                    f"could not be saved: {error}"
                )


    # ========================================================
    # RESULTS
    # ========================================================

    if (
        st.session_state.get(
            "quiz_submitted",
            False
        )
        and
        st.session_state.quiz
    ):

        quiz = st.session_state.quiz

        score = st.session_state.quiz_score

        percentage = (
            st.session_state.quiz_percentage
        )

        st.markdown("---")

        st.subheader(
            "🏆 Quiz Result"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Score",
                f"{score}/{len(quiz)}"
            )

        with col2:

            st.metric(
                "Percentage",
                f"{percentage:.1f}%"
            )


        if percentage >= 80:

            st.success(
                "🎉 Excellent! Strong understanding."
            )

        elif percentage >= 60:

            st.info(
                "👍 Good job! Review the questions "
                "you missed."
            )

        else:

            st.warning(
                "📖 Keep studying and try again."
            )


        # ====================================================
        # REVIEW
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📊 Answer Review"
        )

        for index, question in enumerate(
            quiz
        ):

            correct_number = int(
                question["answer"]
            )

            correct_answer = (
                question["options"][
                    correct_number - 1
                ]
            )

            st.markdown(
                f"### Question {index + 1}"
            )

            # Get submitted radio answer
            selected_answer = st.session_state.get(
    f"quiz_answer_{st.session_state.quiz_id}_{index}"
)

            if (
                selected_answer
                and
                selected_answer == correct_answer
            ):

                st.success(
                    f"✅ Correct — {correct_answer}"
                )

            else:

                st.error(
                    "❌ Incorrect"
                )

                st.write(
                    f"**Your answer:** "
                    f"{selected_answer or 'Not answered'}"
                )

                st.write(
                    f"**Correct answer:** "
                    f"{correct_answer}"
                )

            st.info(
                f"💡 {question['explanation']}"
            )


# ============================================================
# TAB 4 — DASHBOARD
# ============================================================

with tab_dashboard:

    st.header("📊 Learning Dashboard")

    stats = get_statistics()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
        "📝 Quizzes Taken",
        stats["total_quizzes"]
    )

    with col2:

        st.metric(
        "📈 Average Score",
        f"{stats['average_score']:.1f}%"
    )

    with col3:

        st.metric(
        "🏆 Best Score",
        f"{stats['best_score']:.1f}%"
    )

    with col4:

        st.metric(
        "❓ Questions Attempted",
        stats["total_questions"]
    )

    with col5:

        st.metric(
        "📚 Documents",
        len(documents)
    )

    st.markdown("---")

    progress = load_progress()
#========================================================
# PERFORMANCE CHART
#========================================================

if progress:

    st.subheader("📈 Performance Over Time")

    chart_data = pd.DataFrame(
        [
            {
                "Attempt": index + 1,
                "Score": attempt["percentage"]
            }
            for index, attempt in enumerate(progress)
        ]
    )

    chart_data = chart_data.set_index("Attempt")

    st.line_chart(
        chart_data["Score"]
    )

#========================================================
# PER-DOCUMENT PERFORMANCE
#========================================================
if progress:

    st.subheader("📚 Performance by Document")

    document_stats = {}

    for attempt in progress:

        document = attempt["document"]

        if document not in document_stats:
            document_stats[document] = []

        document_stats[document].append(
            attempt["percentage"]
        )

    document_rows = []

    for document, scores in document_stats.items():

        document_rows.append(
            {
                "Document": document,
                "Attempts": len(scores),
                "Average Score": round(
                    sum(scores) / len(scores),
                    1
                ),
                "Best Score": round(
                    max(scores),
                    1
                )
            }
        )

    document_df = pd.DataFrame(
        document_rows
    )

    st.dataframe(
        document_df,
        use_container_width=True,
        hide_index=True
    )

    if not progress:

        st.info(
            "Complete your first quiz to start "
            "tracking your progress."
        )

    else:

        st.subheader(
            "📚 Quiz History"
        )

        for index, attempt in enumerate(
            reversed(progress),
            start=1
        ):

            st.markdown(
                f"### Quiz {index}"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    f"📄 **Document:** "
                    f"{attempt['document']}"
                )

            with col2:

                st.write(
                    f"🎯 **Score:** "
                    f"{attempt['score']}/"
                    f"{attempt['total']}"
                )

            with col3:

                st.write(
                    f"📅 **Date:** "
                    f"{attempt['date']}"
                )

            st.progress(
                min(
                    int(attempt["percentage"]),
                    100
                )
            )

            st.write(
                f"**Result:** "
                f"{attempt['percentage']:.1f}%"
            )

            st.markdown("---")
# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "📚 StudyBuddy • Built with Streamlit, ChromaDB, "
    "Ollama & Qwen 2.5"
)