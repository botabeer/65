"""Game Engine - Unified game loader"""

from games import (
    GuessGame, FastGame, CompatibilityGame, SongGame,
    OppositeGame, ChainGame, LettersGame, CategoryGame,
    HumanAnimalGame, IqGame, ScrambleGame, LetterGame,
    MafiaGame, WordColorGame, RouletteGame, SeenJeemGame
)

class GameEngine:
    GAMES = {
        'خمن': GuessGame,
        'اسرع': FastGame,
        'توافق': CompatibilityGame,
        'اغنيه': SongGame,
        'ضد': OppositeGame,
        'سلسله': ChainGame,
        'تكوين': LettersGame,
        'فئه': CategoryGame,
        'لعبه': HumanAnimalGame,
        'ذكاء': IqGame,
        'ترتيب': ScrambleGame,
        'حروف': LetterGame,
        'مافيا': MafiaGame,
        'لون': WordColorGame,
        'روليت': RouletteGame,
        'سين': SeenJeemGame
    }
    
    @staticmethod
    def create(game_type, line_api, difficulty=3, theme='light'):
        game_class = GameEngine.GAMES.get(game_type)
        if game_class:
            return game_class(line_api, difficulty=difficulty, theme=theme)
        return None
    
    @staticmethod
    def get_available_games():
        return list(GameEngine.GAMES.keys())
