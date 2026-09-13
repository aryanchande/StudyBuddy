import json
from pathlib import Path
from datetime import datetime


PROGRESS_FILE = Path("data/progress.json")


def load_progress():
    """Load saved quiz progress."""

    if not PROGRESS_FILE.exists():
        return []

    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_quiz_result(
    document: str,
    score: int,
    total: int,
    percentage: float
):
    """Save one quiz attempt."""

    PROGRESS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    progress = load_progress()

    attempt = {
        "document": document,
        "score": score,
        "total": total,
        "percentage": round(percentage, 2),
        "date": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    progress.append(attempt)

    with open(
        PROGRESS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            progress,
            file,
            indent=4
        )


def get_statistics():
    """Calculate overall learning statistics."""

    progress = load_progress()

    if not progress:
        return {
            "total_quizzes": 0,
            "average_score": 0,
            "best_score": 0,
            "total_questions": 0
        }

    total_quizzes = len(progress)

    average_score = sum(
        attempt["percentage"]
        for attempt in progress
    ) / total_quizzes

    best_score = max(
        attempt["percentage"]
        for attempt in progress
    )

    total_questions = sum(
        attempt["total"]
        for attempt in progress
    )

    return {
        "total_quizzes": total_quizzes,
        "average_score": round(
            average_score,
            2
        ),
        "best_score": round(
            best_score,
            2
        ),
        "total_questions": total_questions
    }