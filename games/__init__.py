from .song_game import SongGame
from .opposite_game import OppositeGame
from .chain_words_game import ChainGame
from .fast_typing_game import FastGame
from .letters_words_game import LettersGame
from .category_letter_game import CategoryGame
from .human_animal_plant_game import HumanAnimalGame
from .compatibility_game import CompatibilityGame
from .iq_game import IqGame
from .guess_game import GuessGame
from .scramble_word_game import ScrambleGame
from .word_color_game import WordColorGame
from .roulette_game import RouletteGame
from .seen_jeem_game import SeenJeemGame
from .letter_game import LetterGame
from .mafia_game import MafiaGame

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

__all__ = [
    'SongGame', 'OppositeGame', 'ChainGame', 'FastGame',
    'LettersGame', 'CategoryGame', 'HumanAnimalGame',
    'CompatibilityGame', 'IqGame', 'GuessGame', 'ScrambleGame',
    'WordColorGame', 'RouletteGame', 'SeenJeemGame', 'LetterGame',
    'MafiaGame', 'GAMES'
]
