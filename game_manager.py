import importlib
import logging
from config import Config
from database import db

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.game_mappings = {
            "ذكاء": ("games.iq", "IQGame"),
            "خمن": ("games.guess", "GuessGame"),
            "رياضيات": ("games.math", "MathGame"),
            "ترتيب": ("games.scramble", "ScrambleGame"),
            "ضد": ("games.opposite", "OppositeGame"),
            "كتابة": ("games.fast_typing", "FastTypingGame"),
            "سلسلة": ("games.chain_words", "ChainWordsGame"),
            "إنسان": ("games.human_animal", "HumanAnimalGame"),
            "كلمات": ("games.letters_words", "LettersWordsGame"),
            "أغنية": ("games.song", "SongGame"),
            "ألوان": ("games.word_color", "WordColorGame"),
            "توافق": ("games.compatibility", "CompatibilityGame"),
            "مافيا": ("games.mafia", "MafiaGame")
        }

    def normalize_game_cmd(self, cmd: str) -> str:
        """حوّل النص إلى شكل موحد."""
        return Config.normalize(cmd)

    def start_game(self, user_id: str, game_cmd: str, theme="light", group_id: str = None):
        """ابدأ اللعبة إذا كان المستخدم مسجّل."""
        if group_id and not db.is_player_registered(group_id, user_id):
            return None, "يجب أن تكون مسجلاً للمشاركة"

        cmd = self.normalize_game_cmd(game_cmd)
        if cmd not in self.game_mappings:
            return None, "اللعبة غير موجودة"

        module_name, class_name = self.game_mappings[cmd]
        try:
            module = importlib.import_module(module_name)
            game_class = getattr(module, class_name)
            game = game_class(db, theme, user_id=user_id, group_id=group_id)
            db.set_game_progress(user_id, game)
            question = game.start()
            return game, question
        except Exception as e:
            logger.error(f"Error starting game {game_cmd}: {e}")
            return None, "حدث خطأ أثناء بدء اللعبة"

    def process_answer(self, user_id: str, answer: str):
        game = db.get_game_progress(user_id)
        if not game:
            return None, "لا توجد لعبة نشطة"

        result = game.check(answer)
        if result is None:
            # اللعبة انتهت
            score, total, name = game.score, game.total_q, game.game_name
            db.add_points(user_id, score)
            db.increment_games(user_id)
            if score == total:
                db.increment_wins(user_id)
            else:
                db.reset_streak(user_id)
            db.add_game_played(user_id, name)
            achievements = db.check_achievements(user_id)
            db.clear_game_progress(user_id)
            return {
                "finished": True,
                "score": score,
                "total": total,
                "game_name": name,
                "achievements": achievements
            }, None

        question, correct = result
        return question, correct

    def get_hint(self, user_id: str):
        game = db.get_game_progress(user_id)
        return game.get_hint() if game else None

    def reveal_answer(self, user_id: str):
        game = db.get_game_progress(user_id)
        return game.reveal_answer() if game else None

    def stop_game(self, user_id: str):
        game = db.get_game_progress(user_id)
        if not game:
            return 0
        score = game.score
        db.add_points(user_id, score)
        db.reset_streak(user_id)
        db.clear_game_progress(user_id)
        return score

    def count_active(self):
        return len(db._game_progress)
