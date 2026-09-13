import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIR))


# ============================================================
# IMPORTS
# ============================================================

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


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="StudyBuddy",
    page_icon="📚",
    layout="wide"
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


# ============================================================
# HEADER
# ============================================================

st.title("📚 StudyBuddy")

st.subheader(
    "AI-Powered Personalized Learning Assistant"
)

st.write(
    "Upload your study material and use AI to "
    "ask questions, generate summaries, and test "
    "your knowledge."
)


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
                    f"Indexing error: {error}"
                )

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

tab_qa, tab_summary, tab_quiz, tab_dashboard = st.tabs(
    [
        "💬 Ask AI",
        "📝 Summary",
        "🧠 Quiz",
        "📊 Dashboard"
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
                            f"Error: {error}"
                        )


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
                        f"Error generating summary: {error}"
                    )


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
            st.session_state.quiz = None
            st.session_state.quiz_submitted = False
            st.session_state.quiz_score = 0
            st.session_state.quiz_percentage = 0.0

            with st.spinner(
                "🤖 Generating quiz... "
                "This may take a little time."
            ):

                try:

                    quiz = generate_quiz(
                        source=quiz_document_selector,
                        number_of_questions=question_count
                    )

                    # Validate basic response
                    if not quiz:

                        raise ValueError(
                            "The AI returned an empty quiz."
                        )

                    if not isinstance(
                        quiz,
                        list
                    ):

                        raise ValueError(
                            "Invalid quiz format returned by AI."
                        )

                    # Store generated quiz
                    st.session_state.quiz = quiz

                    # Store document separately
                    # from the selectbox widget
                    st.session_state.generated_quiz_document = (
                        quiz_document_selector
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
                key=f"quiz_answer_{index}",
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
                f"quiz_answer_{index}"
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

    col1, col2, col3, col4 = st.columns(4)

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

    st.markdown("---")

    progress = load_progress()

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