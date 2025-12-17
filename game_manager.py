import importlib
import logging

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self, db):
        self.db = db
        self.game_mappings = {
            "ذكاء": ("games.iq", "IQGame"),
            "خمن": ("games.guess", "GuessGame"),
            "رياضيات": ("games.math", "MathGame"),
            "ترتيب": ("games.scramble", "ScrambleGame"),
            "ضد": ("games.opposite", "OppositeGame"),
            "اضداد": ("games.opposite", "OppositeGame"),
            "كتابه": ("games.fast_typing", "FastTypingGame"),
            "كتابة": ("games.fast_typing", "FastTypingGame"),
            "سلسله": ("games.chain_words", "ChainWordsGame"),
            "سلسلة": ("games.chain_words", "ChainWordsGame"),
            "انسان": ("games.human_animal", "HumanAnimalGame"),
            "إنسان": ("games.human_animal", "HumanAnimalGame"),
            "حيوان": ("games.human_animal", "HumanAnimalGame"),
            "كلمات": ("games.letters_words", "LettersWordsGame"),
            "اغنيه": ("games.song", "SongGame"),
            "أغنية": ("games.song", "SongGame"),
            "الوان": ("games.word_color", "WordColorGame"),
            "ألوان": ("games.word_color", "WordColorGame"),
            "توافق": ("games.compatibility", "CompatibilityGame"),
            "مافيا": ("games.mafia", "MafiaGame")
        }
    
    def start_game(self, user_id, game_cmd, theme="light"):
        if game_cmd not in self.game_mappings:
            return None
        
        module_name, class_name = self.game_mappings[game_cmd]
        try:
            module = importlib.import_module(module_name)
            game_class = getattr(module, class_name)
            game = game_class(self.db, theme)
            self.db.set_game_progress(user_id, game)
            return game.start()
        except Exception as e:
            logger.error(f"Error starting game {game_cmd}: {e}")
            return None
    
    def process_answer(self, user_id, answer):
        game = self.db.get_game_progress(user_id)
        if not game:
            return None, None
        
        result = game.check(answer)
        
        if result is None:
            score = game.score
            total = game.total_q
            game_name = game.game_name
            self.db.add_points(user_id, score)
            self.db.increment_games(user_id)
            
            if score == total:
                self.db.increment_wins(user_id)
            else:
                self.db.reset_streak(user_id)
            
            self.db.add_game_played(user_id, game_name)
            achievements = self.db.check_achievements(user_id)
            self.db.clear_game_progress(user_id)
            
            return {
                "finished": True,
                "score": score,
                "total": total,
                "game_name": game_name,
                "achievements": achievements
            }, None
        
        question, correct = result
        return question, correct
    
    def get_hint(self, user_id):
        game = self.db.get_game_progress(user_id)
        if game:
            return game.get_hint()
        return None
    
    def reveal_answer(self, user_id):
        game = self.db.get_game_progress(user_id)
        if game:
            return game.reveal_answer()
        return None
    
    def stop_game(self, user_id):
        game = self.db.get_game_progress(user_id)
        if game:
            score = game.score
            self.db.add_points(user_id, score)
            self.db.reset_streak(user_id)
            self.db.clear_game_progress(user_id)
            return score
        return 0
    
    def count_active(self):
        return len(self.db._game_progress)
