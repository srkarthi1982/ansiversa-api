"""Create only the isolated Quiz attempt lifecycle tables.

Run this explicitly against the configured Quiz database after reviewing the
target environment. Parent Alembic intentionally does not import Quiz metadata.
"""

from app.modules.quiz.db import quiz_engine
from app.modules.quiz.models import QuizAttempt, QuizAttemptQuestion


def main() -> None:
    QuizAttempt.__table__.create(bind=quiz_engine, checkfirst=True)
    QuizAttemptQuestion.__table__.create(bind=quiz_engine, checkfirst=True)
    print("Quiz attempt tables are ready.")


if __name__ == "__main__":
    main()
