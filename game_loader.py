import os, importlib.util, inspect, logging
from typing import Dict, Optional, Type
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseGame(ABC):
    def __init__(self):
        self.name = "Unknown Game"
        self.description = "No description"
        self.min_players = 2
        self.max_players = 20
    
    @abstractmethod
    def start(self, group_id: str, players: Dict) -> tuple[bool, str]:
        pass
    
    @abstractmethod
    def process_message(self, group_id: str, user_id: str, message: str) -> tuple[Optional[str], bool]:
        pass
    
    @abstractmethod
    def end(self, group_id: str) -> tuple[bool, str]:
        pass
    
    @abstractmethod
    def get_status(self, group_id: str) -> str:
        pass

class GameLoader:
    def __init__(self, games_folder: str = 'games'):
        self.games_folder = games_folder
        self.games: Dict[str, Type[BaseGame]] = {}
        self.game_instances: Dict[str, BaseGame] = {}
        if not os.path.exists(games_folder):
            os.makedirs(games_folder)
            logger.info(f"Created games folder: {games_folder}")
    
    def load_games(self) -> int:
        loaded_count = 0
        if not os.path.exists(self.games_folder):
            logger.error(f"Games folder not found: {self.games_folder}")
            return 0
        for filename in os.listdir(self.games_folder):
            if filename.endswith('.py') and not filename.startswith('_'):
                game_path = os.path.join(self.games_folder, filename)
                try:
                    game_name = filename[:-3]
                    spec = importlib.util.spec_from_file_location(game_name, game_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseGame) and obj is not BaseGame:
                            self.games[game_name] = obj
                            logger.info(f"Loaded game: {game_name} ({obj.__name__})")
                            loaded_count += 1
                            break
                except Exception as e:
                    logger.error(f"Failed to load game {filename}: {e}")
        logger.info(f"Loaded {loaded_count} games total")
        return loaded_count
    
    def get_game(self, game_name: str) -> Optional[BaseGame]:
        if game_name not in self.games:
            return None
        if game_name not in self.game_instances:
            self.game_instances[game_name] = self.games[game_name]()
        return self.game_instances[game_name]
    
    def list_games(self) -> Dict[str, str]:
        result = {}
        for game_name in self.games:
            instance = self.get_game(game_name)
            if instance:
                result[game_name] = instance.description
        return result
    
    def game_exists(self, game_name: str) -> bool:
        return game_name in self.games

game_loader = GameLoader()
