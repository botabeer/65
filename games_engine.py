"""
Game Engine - Unified game loader
"""
from games import (
    SongGame, OppositeGame, ChainGame, FastGame,
    LettersGame, CategoryGame, HumanAnimalGame,
    CompatibilityGame, IqGame, GuessGame, ScrambleGame,
    WordColorGame, RouletteGame, SeenJeemGame, LetterGame,
    MafiaGame
)

class GameEngine:
    GAMES = {
        'اغنيه': SongGame,
        'ضد': OppositeGame,
        'سلسله': ChainGame,
        'اسرع': FastGame,
        'تكوين': LettersGame,
        'فئه': CategoryGame,
        'لعبه': HumanAnimalGame,
        'توافق': CompatibilityGame,
        'ذكاء': IqGame,
        'خمن': GuessGame,
        'ترتيب': ScrambleGame,
        'لون': WordColorGame,
        'روليت': RouletteGame,
        'سين': SeenJeemGame,
        'حروف': LetterGame,
        'مافيا': MafiaGame
    }
    
    @staticmethod
    def create(game_type, theme='light'):
        game_class = GameEngine.GAMES.get(game_type)
        if game_class:
            from linebot.v3.messaging import ApiClient, MessagingApi, Configuration
            import os
            config = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
            with ApiClient(config) as api_client:
                line_api = MessagingApi(api_client)
                return game_class(line_api)
        return None
