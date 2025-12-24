import logging
import re
from datetime import datetime
from typing import Dict, Optional
from linebot.v3.messaging import TextMessage

logger = logging.getLogger(__name__)


def normalize_arabic(text):
    """تطبيع النص العربي"""
    if not text:
        return ""
    text = text.strip().lower()
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ؤ': 'و',
        'ئ': 'ي', 'ء': '', 'ة': 'ه', 'ى': 'ي'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    return text.strip()


class GameManager:
    """مدير الألعاب الموحد"""
    
    def __init__(self, line_bot_api):
        self.line_bot_api = line_bot_api
        self.active_games = {}
        self.waiting_for_name = set()
        
        # تعريف الألعاب المتاحة
        self.game_map = {
            'اغنيه': 'SongGame',
            'ضد': 'OppositeGame',
            'سلسله': 'ChainGame',
            'اسرع': 'FastTypingGame',
            'لعبه': 'HumanAnimalGame',
            'تكوين': 'LettersGame',
            'فئه': 'CategoryGame',
            'توافق': 'CompatibilityGame'
        }
    
    def set_waiting_for_name(self, user_id, waiting):
        """تعيين حالة الانتظار للاسم"""
        if waiting:
            self.waiting_for_name.add(user_id)
        else:
            self.waiting_for_name.discard(user_id)
    
    def is_waiting_for_name(self, user_id):
        """التحقق من حالة الانتظار للاسم"""
        return user_id in self.waiting_for_name
    
    def stop_game(self, group_id):
        """إيقاف اللعبة"""
        if group_id in self.active_games:
            del self.active_games[group_id]
            return True
        return False
    
    def process_message(self, text, user_id, group_id, display_name):
        """معالجة رسالة للعبة"""
        text_norm = normalize_arabic(text)
        
        # التحقق من بدء لعبة جديدة
        if text_norm in self.game_map:
            return self._start_game(text_norm, user_id, group_id, display_name)
        
        # معالجة لعبة نشطة
        if group_id in self.active_games:
            return self._process_game_answer(text, user_id, group_id, display_name)
        
        return None
    
    def _start_game(self, game_cmd, user_id, group_id, display_name):
        """بدء لعبة جديدة"""
        try:
            # استيراد ديناميكي للعبة
            game_class_name = self.game_map[game_cmd]
            
            # استيراد من games.unified
            from games.unified import get_game_class
            game_class = get_game_class(game_class_name)
            
            if not game_class:
                return TextMessage(text="اللعبة غير متاحة حالياً")
            
            # إنشاء اللعبة
            game = game_class(self.line_bot_api)
            self.active_games[group_id] = game
            
            # بدء اللعبة
            response = game.start_game()
            return response
            
        except Exception as e:
            logger.error(f"Error starting game: {e}", exc_info=True)
            return TextMessage(text="حدث خطأ في بدء اللعبة")
    
    def _process_game_answer(self, text, user_id, group_id, display_name):
        """معالجة إجابة اللعبة"""
        game = self.active_games.get(group_id)
        if not game:
            return None
        
        try:
            result = game.check_answer(text, user_id, display_name)
            
            if not result:
                return None
            
            responses = []
            
            # رسالة الرد
            if result.get('message'):
                responses.append(TextMessage(text=result['message']))
            
            # الاستجابة الرئيسية
            if result.get('response'):
                responses.append(result['response'])
            
            # السؤال التالي
            if result.get('next_question') and not result.get('game_over'):
                next_q = game.get_question()
                if next_q:
                    responses.append(next_q)
            
            # نهاية اللعبة
            if result.get('game_over'):
                del self.active_games[group_id]
                
                if result.get('points', 0) > 0:
                    from core.database import Database
                    Database.update_user_points(
                        user_id,
                        result['points'],
                        result.get('won', True),
                        game.game_name
                    )
            
            return responses if len(responses) > 1 else (responses[0] if responses else None)
            
        except Exception as e:
            logger.error(f"Error processing answer: {e}", exc_info=True)
            return None
    
    def cleanup_inactive_games(self, timeout_minutes=30):
        """تنظيف الألعاب غير النشطة"""
        try:
            now = datetime.now()
            inactive = []
            
            for group_id, game in self.active_games.items():
                if hasattr(game, 'game_start_time') and game.game_start_time:
                    elapsed = (now - game.game_start_time).total_seconds() / 60
                    if elapsed > timeout_minutes:
                        inactive.append(group_id)
            
            for group_id in inactive:
                del self.active_games[group_id]
            
            return len(inactive)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0
