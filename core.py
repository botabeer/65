from linebot.v3.messaging import TextMessage, FlexMessage
from config import *
from database import db
from game_loader import game_loader
from text_manager import text_manager
from utils import *
from security import sanitize_input
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, line_bot_api, configuration):
        self.api = line_bot_api
        self.config = configuration
        self.user_themes = {}
        self.user_games = {}
    
    def handle_message(self, event):
        try:
            user_id = event.source.user_id
            message_text = event.message.text.strip()
            
            message_text = sanitize_input(message_text)
            
            if not message_text:
                return None
            
            command, args = parse_command(message_text)
            
            is_group = hasattr(event.source, 'group_id')
            group_id = event.source.group_id if is_group else None
            
            theme = self.user_themes.get(user_id, "light")
            
            if command in [normalize_arabic(cmd) for cmd in COMMANDS["text_commands"].keys()]:
                return self._handle_text_command(command, theme)
            
            if command in [normalize_arabic(cmd) for cmd in COMMANDS["general"].keys()]:
                return self._handle_general_command(command, user_id, theme)
            
            if not is_group:
                if game_loader.is_private_game(command):
                    return self._handle_private_game(command, user_id, message_text, theme)
                
                active_game = self.user_games.get(user_id)
                if active_game:
                    return self._process_private_game_answer(user_id, message_text, theme)
            
            if is_group:
                if game_loader.is_group_game(command):
                    return self._handle_group_game(command, group_id, user_id, message_text, theme)
                
                group_cmd = normalize_arabic(command)
                if group_cmd in [normalize_arabic(cmd) for cmd in COMMANDS["group_controls"].keys()]:
                    return self._handle_group_control(command, group_id, user_id, args, theme)
                
                return self._handle_group_game_message(group_id, user_id, message_text, theme)
            
            return None
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return None
    
    def _handle_text_command(self, command, theme):
        content = text_manager.get_content(command)
        return [TextMessage(text=content)]
    
    def _handle_general_command(self, command, user_id, theme):
        if command == normalize_arabic("ثيم"):
            current_theme = self.user_themes.get(user_id, "light")
            new_theme = "dark" if current_theme == "light" else "light"
            self.user_themes[user_id] = new_theme
            
            theme_name = "الداكن" if new_theme == "dark" else "الفاتح"
            return [TextMessage(text=f"تم التغيير إلى الثيم {theme_name}")]
        
        elif command == normalize_arabic("مساعده"):
            return self._create_help_message(theme)
        
        elif command == normalize_arabic("معلومات"):
            info_text = f"{BOT_NAME} v{BOT_VERSION}\n{BOT_CREATOR}\n\n"
            info_text += f"الألعاب المتاحة: {len(game_loader.games)}\n"
            info_text += "اكتب مساعده لعرض الأوامر"
            return [TextMessage(text=info_text)]
        
        elif command == normalize_arabic("ابدا"):
            welcome_text = f"مرحبا بك في {BOT_NAME}\n\n"
            welcome_text += "للعب: اختر لعبة من القائمة\n"
            welcome_text += "للمساعدة: اكتب مساعده\n"
            welcome_text += "تغيير الثيم: اكتب ثيم"
            return [TextMessage(text=welcome_text)]
        
        return None
    
    def _handle_private_game(self, command, user_id, message_text, theme):
        game_class = game_loader.get_game_class(command)
        
        if not game_class:
            return [TextMessage(text=MESSAGES["game_not_found"])]
        
        try:
            game = game_class(db, theme)
            question = game.start()
            
            self.user_games[user_id] = game
            
            return [FlexMessage(alt_text="سؤال", contents=question["contents"])]
        
        except Exception as e:
            logger.error(f"Error starting private game: {e}", exc_info=True)
            return [TextMessage(text="حدث خطأ في بدء اللعبة")]
    
    def _process_private_game_answer(self, user_id, answer, theme):
        game = self.user_games.get(user_id)
        
        if not game:
            return None
        
        try:
            normalized_cmd = normalize_arabic(answer)
            
            if normalized_cmd == normalize_arabic("ايقاف"):
                del self.user_games[user_id]
                result_text = f"تم إيقاف اللعبة\n\nالنتيجة: {game.score}/{game.total_q}"
                return [TextMessage(text=result_text)]
            
            if normalized_cmd == normalize_arabic("لمح") or normalized_cmd == normalize_arabic("تلميح"):
                if game.supports_hint:
                    hint = game.get_hint()
                    if hint:
                        return [FlexMessage(alt_text="تلميح", contents=hint["contents"])]
                return [TextMessage(text="التلميح غير متاح")]
            
            if normalized_cmd == normalize_arabic("جاوب") or normalized_cmd == normalize_arabic("الاجابه"):
                if game.supports_reveal:
                    reveal = game.reveal_answer()
                    if reveal:
                        result = game.check(answer)
                        if result is None:
                            del self.user_games[user_id]
                            return [
                                FlexMessage(alt_text="الإجابة", contents=reveal["contents"]),
                                TextMessage(text=f"انتهت اللعبة\n\nالنتيجة: {game.score}/{game.total_q}")
                            ]
                        return [FlexMessage(alt_text="الإجابة", contents=reveal["contents"])]
                return [TextMessage(text="عرض الإجابة غير متاح")]
            
            result = game.check(answer)
            
            if result is None:
                del self.user_games[user_id]
                final_result = format_game_result(game.game_name, game.score, game.total_q, theme)
                return [FlexMessage(alt_text="النتيجة", contents=final_result["contents"])]
            
            question, correct = result
            
            if correct:
                feedback = TextMessage(text="صحيح")
            else:
                feedback = TextMessage(text="خطأ")
            
            return [
                feedback,
                FlexMessage(alt_text="سؤال", contents=question["contents"])
            ]
        
        except Exception as e:
            logger.error(f"Error processing answer: {e}", exc_info=True)
            del self.user_games[user_id]
            return [TextMessage(text="حدث خطأ")]
    
    def _handle_group_game(self, command, group_id, user_id, message_text, theme):
        session = db.get_session(group_id)
        if session and session.is_active:
            return [TextMessage(text="يوجد لعبة نشطة بالفعل. اكتب انهاء لإنهائها")]
        
        game_class = game_loader.get_game_class(command)
        
        if not game_class:
            return [TextMessage(text=MESSAGES["game_not_found"])]
        
        try:
            game_instance = game_class()
            game_name = game_instance.name
            
            session = db.create_session(group_id, command)
            
            if not session:
                return [TextMessage(text="فشل في إنشاء الجلسة")]
            
            register_text = f"{game_name}\n\n"
            register_text += f"{game_instance.description}\n\n"
            register_text += f"عدد اللاعبين: {game_instance.min_players}-{game_instance.max_players}\n\n"
            register_text += "للتسجيل: تسجيل [اسمك]\n"
            register_text += "مثال: تسجيل احمد"
            
            return [TextMessage(text=register_text)]
        
        except Exception as e:
            logger.error(f"Error starting group game: {e}", exc_info=True)
            return [TextMessage(text="حدث خطأ في بدء اللعبة")]
    
    def _handle_group_control(self, command, group_id, user_id, args, theme):
        if command == normalize_arabic("تسجيل"):
            if not args:
                return [TextMessage(text="استخدام: تسجيل [اسمك]")]
            
            valid, result = validate_player_name(args)
            if not valid:
                return [TextMessage(text=result)]
            
            success = db.add_player(group_id, user_id, args)
            
            if success:
                session = db.get_session(group_id)
                game_class = game_loader.get_game_class(session.game_name)
                game_instance = game_class()
                
                text = f"تم تسجيل {args} بنجاح\n"
                text += f"اللاعبون: {len(session.players)}/{game_instance.max_players}"
                
                if len(session.players) >= game_instance.min_players:
                    success, start_msg = game_instance.start(group_id, session.players)
                    if success:
                        text += f"\n\n{start_msg}"
                
                return [TextMessage(text=text)]
            else:
                return [TextMessage(text="أنت مسجل بالفعل أو اللعبة غير نشطة")]
        
        elif command == normalize_arabic("حاله"):
            session = db.get_session(group_id)
            
            if not session:
                return [TextMessage(text="لا توجد لعبة نشطة")]
            
            status_text = f"اللعبة: {session.game_name}\n"
            status_text += f"اللاعبون: {len(session.players)}\n\n"
            
            for player in session.players.values():
                status_text += f"{player.display_name}: {player.score}\n"
            
            return [TextMessage(text=status_text)]
        
        elif command == normalize_arabic("صداره"):
            leaders = db.get_leaderboard(group_id, limit=10)
            
            if not leaders:
                return [TextMessage(text="لا يوجد لاعبون بعد")]
            
            return [FlexMessage(
                alt_text="لوحة الصدارة",
                contents=format_leaderboard(leaders, theme)["contents"]
            )]
        
        elif command == normalize_arabic("انهاء"):
            session = db.get_session(group_id)
            
            if not session:
                return [TextMessage(text="لا توجد لعبة نشطة")]
            
            game_class = game_loader.get_game_class(session.game_name)
            game_instance = game_class()
            
            success, end_msg = game_instance.end(group_id)
            
            db.delete_session(group_id)
            
            return [TextMessage(text=end_msg)]
        
        return None
    
    def _handle_group_game_message(self, group_id, user_id, message_text, theme):
        session = db.get_session(group_id)
        
        if not session or not session.is_active:
            return None
        
        if not db.is_player_registered(group_id, user_id):
            return None
        
        game_class = game_loader.get_game_class(session.game_name)
        
        if not game_class:
            return None
        
        try:
            game_instance = game_class()
            response, should_reply = game_instance.process_message(group_id, user_id, message_text)
            
            if should_reply and response:
                return [TextMessage(text=response)]
        
        except Exception as e:
            logger.error(f"Error processing group game message: {e}", exc_info=True)
        
        return None
    
    def _create_help_message(self, theme):
        help_text = f"{BOT_NAME} - دليل الاستخدام\n\n"
        help_text += "الألعاب الفردية:\n"
        help_text += "ذكاء - خمن - ترتيب - ضد\n"
        help_text += "كتابه - انسان - كلمات\n"
        help_text += "اغنيه - توافق\n\n"
        help_text += "الألعاب الجماعية:\n"
        help_text += "سلسله - الوان - مافيا\n\n"
        help_text += "أوامر النصوص:\n"
        help_text += "تحدي - اعتراف - منشن\n"
        help_text += "شخصيه - سؤال - حكمه - موقف\n\n"
        help_text += "أوامر أخرى:\n"
        help_text += "ثيم - معلومات - ابدا\n\n"
        help_text += f"{BOT_CREATOR}"
        
        return [TextMessage(text=help_text)]
