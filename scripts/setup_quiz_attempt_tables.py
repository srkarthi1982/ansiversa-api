"""Apply the isolated Quiz Alembic migrations.

Run this explicitly against the configured Quiz database after reviewing the
target environment. Parent Alembic intentionally does not import Quiz metadata.
"""

from alembic import command
from alembic.config import Config


def main() -> None:
    command.upgrade(Config("quiz_alembic.ini"), "head")
    print("Quiz database migrations are at head.")


if __name__ == "__main__":
    main()
