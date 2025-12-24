import random
from games.base import BaseGame


class CompatibilityGame(BaseGame):
    def __init__(self, db, theme="light"):
        super().__init__(db, theme)
        self.game_name = "لعبة التوافق"
        self.supports_hint = False
        self.supports_reveal = False
        self.total_q = 1

    def get_question(self):
        question = "اكتب اسمين مع (و) بينهما\nمثال: احمد و سارة"
        return self.build_question_flex(question, None)

    def check_answer(self, answer: str) -> bool:
        if "و" not in answer:
            return False

        parts = (
            answer.replace(" و ", "|")
            .replace(" و", "|")
            .replace("و ", "|")
            .split("|")
        )

        if len(parts) != 2:
            return False

        name1, name2 = parts[0].strip(), parts[1].strip()
        if not name1 or not name2:
            return False

        percentage = self._calculate_compatibility(name1, name2)
        message = self._get_message(percentage)

        self.current_answer = (
            f"{name1} و {name2}\n"
            f"نسبة التوافق: {percentage}%\n{message}"
        )
        return True

    def _calculate_compatibility(self, name1, name2):
        seed = sum(ord(c) for c in (name1 + name2))
        random.seed(seed)
        return random.randint(20, 100)

    def _get_message(self, percentage):
        if percentage >= 90:
            return "توافق ممتاز جدا"
        if percentage >= 75:
            return "توافق رائع"
        if percentage >= 60:
            return "توافق جيد"
        if percentage >= 45:
            return "توافق متوسط"
        return "توافق ضعيف"

    def finish(self):
        return None
