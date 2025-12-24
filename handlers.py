from linebot.models import TextSendMessage, MessageEvent, TextMessage
from database import db
from game_loader import game_loader
from security import security
from config import MESSAGES, OWNER_USER_ID, BOT_NAME
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, line_bot_api):
        self.bot = line_bot_api
    
    def handle_message(self, event: MessageEvent) -> list:
        if not isinstance(event.message, TextMessage):
            return []
        
        text = security.sanitize_input(event.message.text)
        user_id = event.source.user_id
        
        is_allowed, spam_msg = security.check_spam(user_id)
        if not is_allowed:
            return [TextSendMessage(text=spam_msg)] if spam_msg else []
        
        is_group = hasattr(event.source, 'group_id')
        group_id = event.source.group_id if is_group else None
        
        try:
            profile = self.bot.get_profile(user_id)
            display_name = profile.display_name
        except:
            display_name = "مستخدم"
        
        if text.startswith('/'):
            return self._handle_command(event, text, user_id, group_id, display_name, is_group)
        
        if is_group and group_id and db.is_player_registered(group_id, user_id):
            return self._handle_game_message(group_id, user_id, text)
        
        return []
    
    def _handle_command(self, event, text, user_id, group_id, display_name, is_group):
        parts = text.lower().split()
        command = parts[0]
        
        if command in ['/تسجيل', '/join']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            return self._cmd_register(user_id, group_id, display_name)
        
        elif command in ['/انسحاب', '/leave']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            return self._cmd_leave(user_id, group_id)
        
        elif command in ['/العاب', '/games']:
            return self._cmd_list_games()
        
        elif command in ['/اختر', '/select']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            if len(parts) < 2:
                return [TextSendMessage(text="الاستخدام: /اختر اسم_اللعبة")]
            return self._cmd_select_game(group_id, parts[1])
        
        elif command in ['/بدء', '/start']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            return self._cmd_start_game(group_id)
        
        elif command in ['/سؤال', '/next']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            return self._cmd_next_question(group_id)
        
        elif command in ['/انهاء', '/end']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            return self._cmd_end_game(group_id)
        
        elif command in ['/نقاط', '/score']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            return self._cmd_scoreboard(group_id)
        
        elif command in ['/لاعبين', '/players']:
            if not is_group:
                return [TextSendMessage(text="هذا الأمر للمجموعات فقط")]
            return self._cmd_list_players(group_id)
        
        elif command in ['/مساعدة', '/help']:
            return self._cmd_help()
        
        elif command in ['/حظر', '/ban']:
            if not security.is_owner(user_id):
                return []
            return self._cmd_ban(parts)
        
        elif command in ['/فك_حظر', '/unban']:
            if not security.is_owner(user_id):
                return []
            return self._cmd_unban(parts)
        
        elif command in ['/اضافة_ادمن', '/addadmin']:
            if not security.is_owner(user_id):
                return []
            return self._cmd_add_admin(parts)
        
        elif command in ['/حذف_ادمن', '/removeadmin']:
            if not security.is_owner(user_id):
                return []
            return self._cmd_remove_admin(parts)
        
        return []
    
    def _cmd_register(self, user_id, group_id, display_name):
        if db.is_player_registered(group_id, user_id):
            return []
        
        session = db.get_session(group_id)
        if not session:
            return [TextSendMessage(text="يجب اختيار لعبة اولا\nاستخدم /العاب لعرض الألعاب")]
        
        if db.add_player(group_id, user_id, display_name):
            count = len(session.players)
            return [TextSendMessage(text=f"{display_name} {MESSAGES['registration_success']}\nعدد اللاعبين: {count}")]
        
        return []
    
    def _cmd_leave(self, user_id, group_id):
        if db.is_player_registered(group_id, user_id):
            db.remove_player(group_id, user_id)
        return []
    
    def _cmd_list_games(self):
        games = game_loader.list_games()
        
        if not games:
            return [TextSendMessage(text="لا توجد العاب متاحة")]
        
        text = f"{BOT_NAME}\nالألعاب المتاحة:\n\n"
        for i, (name, desc) in enumerate(games.items(), 1):
            text += f"{i}. {name}\n{desc}\n\n"
        
        text += "استخدم: /اختر اسم_اللعبة"
        
        return [TextSendMessage(text=text)]
    
    def _cmd_select_game(self, group_id, game_name):
        if not game_loader.game_exists(game_name):
            return [TextSendMessage(text=MESSAGES['game_not_found'])]
        
        session = db.get_session(group_id)
        if session and session.is_active:
            return [TextSendMessage(text="يوجد لعبة نشطة\nاستخدم /انهاء اولا")]
        
        db.create_session(group_id, game_name)
        game = game_loader.get_game(game_name)
        
        return [TextSendMessage(text=f"تم اختيار: {game.name}\n{game.description}\n\nاستخدم /تسجيل للانضمام")]
    
    def _cmd_start_game(self, group_id):
        session = db.get_session(group_id)
        
        if not session:
            return [TextSendMessage(text="يجب اختيار لعبة اولا")]
        
        if session.is_active:
            return [TextSendMessage(text="اللعبة نشطة بالفعل")]
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return [TextSendMessage(text=MESSAGES['game_not_found'])]
        
        success, message = game.start(group_id, session.players)
        
        if success:
            session.is_active = True
        
        return [TextSendMessage(text=message)]
    
    def _cmd_next_question(self, group_id):
        session = db.get_session(group_id)
        
        if not session or not session.is_active:
            return [TextSendMessage(text=MESSAGES['no_active_game'])]
        
        game = game_loader.get_game(session.game_name)
        if not game or not hasattr(game, 'next_question'):
            return [TextSendMessage(text="هذه اللعبة لا تدعم هذا الأمر")]
        
        success, message = game.next_question(group_id)
        return [TextSendMessage(text=message)]
    
    def _cmd_end_game(self, group_id):
        session = db.get_session(group_id)
        
        if not session or not session.is_active:
            return [TextSendMessage(text=MESSAGES['no_active_game'])]
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return [TextSendMessage(text=MESSAGES['game_not_found'])]
        
        success, message = game.end(group_id)
        
        if success:
            session.is_active = False
        
        return [TextSendMessage(text=message)]
    
    def _cmd_scoreboard(self, group_id):
        session = db.get_session(group_id)
        
        if not session:
            return [TextSendMessage(text="لا توجد لعبة")]
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return [TextSendMessage(text=MESSAGES['game_not_found'])]
        
        message = game.get_status(group_id)
        return [TextSendMessage(text=message)]
    
    def _cmd_list_players(self, group_id):
        session = db.get_session(group_id)
        
        if not session or not session.players:
            return [TextSendMessage(text="لا يوجد لاعبون")]
        
        text = "اللاعبون المسجلون:\n"
        for i, player in enumerate(session.players.values(), 1):
            text += f"{i}. {player.display_name}\n"
        
        return [TextSendMessage(text=text)]
    
    def _cmd_help(self):
        help_text = f"""{BOT_NAME}

الأوامر الأساسية:
/العاب - عرض الألعاب المتاحة
/اختر اسم_اللعبة - اختيار لعبة
/تسجيل - التسجيل في اللعبة
/انسحاب - الانسحاب
/لاعبين - قائمة اللاعبين

اوامر اللعب:
/بدء - بدء اللعبة
/سؤال - السؤال التالي
/نقاط - عرض النقاط
/انهاء - انهاء اللعبة

/مساعدة - عرض هذه الرسالة"""
        
        return [TextSendMessage(text=help_text)]
    
    def _cmd_ban(self, parts):
        if len(parts) < 2:
            return [TextSendMessage(text="الاستخدام: /حظر USER_ID")]
        
        user_id = parts[1]
        from config import SECURITY_SETTINGS
        db.ban_user(user_id, SECURITY_SETTINGS['ban_duration'])
        logger.info(f"User {user_id} banned by owner")
        return [TextSendMessage(text=f"تم حظر {user_id}")]
    
    def _cmd_unban(self, parts):
        if len(parts) < 2:
            return [TextSendMessage(text="الاستخدام: /فك_حظر USER_ID")]
        
        user_id = parts[1]
        db.unban_user(user_id)
        logger.info(f"User {user_id} unbanned by owner")
        return [TextSendMessage(text=f"تم فك حظر {user_id}")]
    
    def _cmd_add_admin(self, parts):
        if len(parts) < 2:
            return [TextSendMessage(text="الاستخدام: /اضافة_ادمن USER_ID")]
        
        user_id = parts[1]
        db.add_admin(user_id)
        logger.info(f"User {user_id} added as admin")
        return [TextSendMessage(text=f"تم اضافة {user_id} كأدمن")]
    
    def _cmd_remove_admin(self, parts):
        if len(parts) < 2:
            return [TextSendMessage(text="الاستخدام: /حذف_ادمن USER_ID")]
        
        user_id = parts[1]
        db.remove_admin(user_id)
        logger.info(f"User {user_id} removed from admins")
        return [TextSendMessage(text=f"تم حذف {user_id} من الأدمنز")]
    
    def _handle_game_message(self, group_id, user_id, text):
        session = db.get_session(group_id)
        
        if not session or not session.is_active:
            return []
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return []
        
        response, should_reply = game.process_message(group_id, user_id, text)
        
        if should_reply and response:
            return [TextSendMessage(text=response)]
        
        return []
