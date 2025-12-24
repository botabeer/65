import importlib
import os
import logging
from config import COMMANDS, normalize_arabic

logger = logging.getLogger(__name__)

class GameLoader:
    """محمل الألعاب الديناميكي"""
    
    def __init__(self):
        self.games = {}
        self.private_games = {}
        self.group_games = {}
    
    def load_games(self):
        """تحميل جميع الألعاب من مجلد games"""
        games_loaded = 0
        
        # تحميل الألعاب الفردية
        for game_cmd, game_class_name in COMMANDS["private_games"].items():
            try:
                module_name = self._get_module_name(game_class_name)
                module = importlib.import_module(f"games.{module_name}")
                game_class = getattr(module, game_class_name)
                
                self.private_games[normalize_arabic(game_cmd)] = game_class
                games_loaded += 1
                
                logger.info(f"Loaded private game: {game_cmd} -> {game_class_name}")
            
            except Exception as e:
                logger.error(f"Failed to load private game {game_cmd}: {e}")
        
        # تحميل الألعاب الجماعية
        for game_cmd, game_class_name in COMMANDS["group_games"].items():
            try:
                module_name = self._get_module_name(game_class_name)
                module = importlib.import_module(f"games.{module_name}")
                game_class = getattr(module, game_class_name)
                
                self.group_games[normalize_arabic(game_cmd)] = game_class
                games_loaded += 1
                
                logger.info(f"Loaded group game: {game_cmd} -> {game_class_name}")
            
            except Exception as e:
                logger.error(f"Failed to load group game {game_cmd}: {e}")
        
        # دمج الألعاب
        self.games = {**self.private_games, **self.group_games}
        
        logger.info(f"Total games loaded: {games_loaded}")
        return games_loaded
    
    def _get_module_name(self, class_name):
        """استخراج اسم الموديول من اسم الكلاس"""
        # تحويل من CamelCase إلى snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        name = name.replace('_game', '')
        return name
    
    def get_game_class(self, game_cmd):
        """الحصول على كلاس اللعبة"""
        normalized_cmd = normalize_arabic(game_cmd)
        return self.games.get(normalized_cmd)
    
    def is_private_game(self, game_cmd):
        """التحقق إذا كانت اللعبة خاصة (فردية)"""
        normalized_cmd = normalize_arabic(game_cmd)
        return normalized_cmd in self.private_games
    
    def is_group_game(self, game_cmd):
        """التحقق إذا كانت اللعبة جماعية"""
        normalized_cmd = normalize_arabic(game_cmd)
        return normalized_cmd in self.group_games
    
    def get_all_games_list(self):
        """الحصول على قائمة بجميع الألعاب"""
        return list(self.games.keys())


# مثيل عام
game_loader = GameLoader()


# ===== Base Game Class =====
class BaseGame:
    """الكلاس الأساسي لجميع الألعاب"""
    
    def __init__(self):
        self.name = "لعبة"
        self.description = ""
        self.min_players = 1
        self.max_players = 1
        self.is_group_game = False
    
    def start(self, group_id: str, players: dict) -> tuple[bool, str]:
        """
        بدء اللعبة
        Returns: (success: bool, message: str)
        """
        raise NotImplementedError
    
    def process_message(self, group_id: str, user_id: str, message: str) -> tuple[str, bool]:
        """
        معالجة رسالة من لاعب
        Returns: (response: str, should_reply: bool)
        """
        raise NotImplementedError
    
    def end(self, group_id: str) -> tuple[bool, str]:
        """
        إنهاء اللعبة
        Returns: (success: bool, message: str)
        """
        raise NotImplementedError
    
    def get_status(self, group_id: str) -> str:
        """الحصول على حالة اللعبة"""
        return "لا توجد معلومات"
