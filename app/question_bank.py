from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any


DIFFICULTIES = ("easy", "medium", "hard")
REQUIRED_FIELDS = {"id", "category", "difficulty", "prompt", "options", "answerIndex"}


class QuestionBankError(ValueError):
    pass


class QuestionBank:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._questions: list[dict[str, Any]] = []
        self._by_id: dict[str, dict[str, Any]] = {}
        self.loaded_at = 0.0

    def load(self) -> dict[str, Any]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise QuestionBankError("Question bank must be a JSON array.")

        seen_ids: set[str] = set()
        questions: list[dict[str, Any]] = []

        for index, item in enumerate(raw, start=1):
            if not isinstance(item, dict):
                raise QuestionBankError(f"Question #{index} must be an object.")

            missing = REQUIRED_FIELDS - set(item)
            if missing:
                missing_list = ", ".join(sorted(missing))
                raise QuestionBankError(f"Question #{index} is missing: {missing_list}.")

            question_id = str(item["id"]).strip()
            if not question_id:
                raise QuestionBankError(f"Question #{index} has an empty id.")
            if question_id in seen_ids:
                raise QuestionBankError(f"Duplicate question id: {question_id}.")
            seen_ids.add(question_id)

            difficulty = str(item["difficulty"]).strip().lower()
            if difficulty not in DIFFICULTIES:
                raise QuestionBankError(
                    f"{question_id} has invalid difficulty '{item['difficulty']}'."
                )

            options = item["options"]
            if not isinstance(options, list) or len(options) != 4:
                raise QuestionBankError(f"{question_id} must have exactly 4 options.")

            answer_index = item["answerIndex"]
            if not isinstance(answer_index, int) or not 0 <= answer_index < len(options):
                raise QuestionBankError(f"{question_id} has an invalid answerIndex.")

            raw_tags = item.get("tags", [])
            tags = (
                [str(tag).strip() for tag in raw_tags if str(tag).strip()]
                if isinstance(raw_tags, list)
                else []
            )

            normalized = {
                "id": question_id,
                "category": str(item["category"]).strip(),
                "difficulty": difficulty,
                "prompt": str(item["prompt"]).strip(),
                "options": [str(option).strip() for option in options],
                "answerIndex": answer_index,
                "explanation": str(item.get("explanation", "")).strip(),
                "tags": tags,
            }

            if not normalized["category"]:
                raise QuestionBankError(f"{question_id} has an empty category.")
            if not normalized["prompt"]:
                raise QuestionBankError(f"{question_id} has an empty prompt.")
            if any(not option for option in normalized["options"]):
                raise QuestionBankError(f"{question_id} has an empty option.")

            questions.append(normalized)

        self._questions = questions
        self._by_id = {question["id"]: question for question in questions}
        self.loaded_at = time.time()
        return self.stats()

    def get(self, question_id: str) -> dict[str, Any] | None:
        return self._by_id.get(question_id)

    def pick(
        self,
        difficulty: str,
        seen_ids: set[str],
        categories: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        if not self._questions:
            raise QuestionBankError("Question bank is empty.")

        category_set = set(categories or ())
        scoped_questions = [
            question
            for question in self._questions
            if not category_set or question["category"] in category_set
        ]
        if not scoped_questions:
            scoped_questions = self._questions

        candidates = [
            question
            for question in scoped_questions
            if question["difficulty"] == difficulty and question["id"] not in seen_ids
        ]

        if not candidates:
            candidates = [
                question
                for question in scoped_questions
                if question["id"] not in seen_ids
            ]

        if not candidates:
            seen_ids.clear()
            candidates = [
                question
                for question in scoped_questions
                if question["difficulty"] == difficulty
            ] or scoped_questions

        return random.choice(candidates)

    def stats(self) -> dict[str, Any]:
        categories: dict[str, dict[str, int]] = {}
        difficulties = {difficulty: 0 for difficulty in DIFFICULTIES}

        for question in self._questions:
            category = question["category"]
            difficulty = question["difficulty"]
            categories.setdefault(
                category, {known_difficulty: 0 for known_difficulty in DIFFICULTIES}
            )
            categories[category][difficulty] += 1
            difficulties[difficulty] += 1

        return {
            "total": len(self._questions),
            "categories": categories,
            "difficulties": difficulties,
            "loadedAt": int(self.loaded_at * 1000),
        }


def public_question(question: dict[str, Any]) -> dict[str, Any]:
    result = {
        "id": question["id"],
        "category": question["category"],
        "difficulty": question["difficulty"],
        "prompt": question["prompt"],
        "options": question["options"],
        "tags": question.get("tags", []),
    }
    return result
