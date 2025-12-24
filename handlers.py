from linebot.v3.messaging import TextMessage, FlexMessage, ApiClient, MessagingApi
from database import db
from game_loader import game_loader
from security import security
from config import MESSAGES, BOT_NAME, Config
from text_manager import text_manager
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, line_bot_api, configuration):
        self.bot = line_bot_api
        self.configuration = configuration
        self.user_themes = {}
    
    def _get_profile(self, user_id):
        try:
            with ApiClient(self.configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                profile = line_bot_api.get_profile(user_id)
                return profile.display_name
        except:
            return "مستخدم"
    
    def _get_theme(self, user_id):
        return self.user_themes.get(user_id, "light")
    
    def _toggle_theme(self, user_id):
        current = self._get_theme(user_id)
        new_theme = "dark" if current == "light" else "light"
        self.user_themes[user_id] = new_theme
        return new_theme
    
    def handle_message(self, event):
        if not isinstance(event.message, type(event.message)):
            return []
        
        text = security.sanitize_input(event.message.text).strip()
        user_id = event.source.user_id
        
        is_allowed, spam_msg = security.check_spam(user_id)
        if not is_allowed:
            return [TextMessage(text=spam_msg)] if spam_msg else []
        
        is_group = hasattr(event.source, 'group_id')
        group_id = event.source.group_id if is_group else None
        display_name = self._get_profile(user_id)
        theme = self._get_theme(user_id)
        
        normalized = Config.normalize(text)
        
        # أوامر النصوص (تعمل بدون تسجيل)
        txt_content = text_manager.get_content(normalized)
        if txt_content:
            return [self._build_text_card(txt_content, normalized, theme)]
        
        # التحقق من الأوامر
        if normalized in ['بدايه', 'بداية', 'القائمة', 'قائمه']:
            return [FlexMessage(alt_text="القائمة", contents=self._main_menu(theme))]
        
        elif normalized in ['العاب', 'الالعاب']:
            return [FlexMessage(alt_text="الألعاب", contents=self._games_menu(theme))]
        
        elif normalized in ['ثيم', 'الثيم']:
            new_theme = self._toggle_theme(user_id)
            theme_name = "الداكن" if new_theme == "dark" else "الفاتح"
            return [FlexMessage(alt_text="الثيم", contents=self._theme_changed(theme_name, new_theme))]
        
        elif normalized in ['مساعده', 'مساعدة']:
            return [FlexMessage(alt_text="المساعدة", contents=self._help_menu(theme))]
        
        # أوامر المجموعات
        if not is_group:
            return [TextMessage(text=MESSAGES['group_only'])]
        
        if normalized in ['تسجيل', 'انضم']:
            return self._cmd_register(user_id, group_id, display_name, theme)
        
        elif normalized in ['انسحاب', 'انسحب']:
            return self._cmd_leave(user_id, group_id, display_name, theme)
        
        elif normalized in game_loader.games.keys():
            return self._cmd_select_game(group_id, normalized, theme)
        
        elif normalized in ['بدء', 'ابدا', 'ابدأ']:
            return self._cmd_start_game(group_id, theme)
        
        elif normalized in ['انهاء', 'انهي', 'ايقاف']:
            return self._cmd_end_game(group_id, theme)
        
        elif normalized in ['نقاط', 'النقاط']:
            return self._cmd_scoreboard(group_id, theme)
        
        elif normalized in ['لاعبين', 'اللاعبين']:
            return self._cmd_list_players(group_id, theme)
        
        # معالجة رسائل اللعبة
        session = db.get_session(group_id)
        if session and session.is_active and db.is_player_registered(group_id, user_id):
            return self._handle_game_message(group_id, user_id, text, theme)
        
        return []
    
    def _build_text_card(self, content, cmd_type, theme):
        c = Config.THEMES[theme]
        
        titles = {
            'تحدي': 'تحدي',
            'اعتراف': 'اعتراف',
            'منشن': 'منشن',
            'شخصيه': 'سؤال شخصي',
            'شخصية': 'سؤال شخصي',
            'سؤال': 'سؤال',
            'حكمه': 'حكمة',
            'حكمة': 'حكمة',
            'موقف': 'موقف'
        }
        
        title = titles.get(cmd_type, 'محتوى')
        
        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": title,
                        "size": "xl",
                        "weight": "bold",
                        "color": c["primary"]
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": content,
                        "size": "lg",
                        "wrap": True,
                        "color": c["text"],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
        
        return FlexMessage(alt_text=title, contents=bubble)
    
    def _main_menu(self, theme):
        c = Config.THEMES[theme]
        
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": BOT_NAME,
                        "size": "xxl",
                        "weight": "bold",
                        "color": c["primary"],
                        "align": "center"
                    },
                    {
                        "type": "separator",
                        "margin": "lg",
                        "color": c["border"]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "الألعاب", "text": "العاب"},
                                "style": "primary",
                                "color": c["primary"],
                                "height": "md"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "تحدي", "text": "تحدي"},
                                "style": "secondary",
                                "color": c["success"],
                                "height": "md",
                                "margin": "md"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "اعتراف", "text": "اعتراف"},
                                "style": "secondary",
                                "color": c["info"],
                                "height": "md",
                                "margin": "md"
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "سؤال", "text": "سؤال"},
                                "style": "secondary",
                                "color": c["warning"],
                                "height": "md",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "حكمة", "text": "حكمه"},
                                        "style": "secondary",
                                        "color": c["secondary"],
                                        "height": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "موقف", "text": "موقف"},
                                        "style": "secondary",
                                        "color": c["secondary"],
                                        "height": "sm",
                                        "flex": 1
                                    }
                                ],
                                "spacing": "sm",
                                "margin": "md"
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "تغيير الثيم", "text": "ثيم"},
                                        "style": "secondary",
                                        "color": c["danger"],
                                        "height": "sm",
                                        "flex": 1
                                    },
                                    {
                                        "type": "button",
                                        "action": {"type": "message", "label": "مساعدة", "text": "مساعده"},
                                        "style": "secondary",
                                        "color": c["text_secondary"],
                                        "height": "sm",
                                        "flex": 1
                                    }
                                ],
                                "spacing": "sm",
                                "margin": "md"
                            }
                        ],
                        "margin": "lg"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
    
    def _games_menu(self, theme):
        c = Config.THEMES[theme]
        games = game_loader.list_games()
        
        contents = [
            {
                "type": "text",
                "text": "اختر لعبة",
                "size": "xl",
                "weight": "bold",
                "color": c["primary"]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]
        
        for game_name, desc in games.items():
            contents.append({
                "type": "button",
                "action": {"type": "message", "label": desc, "text": game_name},
                "style": "primary",
                "color": c["primary"],
                "height": "md",
                "margin": "md"
            })
        
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
    
    def _theme_changed(self, theme_name, theme):
        c = Config.THEMES[theme]
        
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"تم التبديل للثيم {theme_name}",
                        "size": "lg",
                        "weight": "bold",
                        "color": c["success"],
                        "align": "center"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
    
    def _help_menu(self, theme):
        c = Config.THEMES[theme]
        
        return {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "المساعدة",
                        "size": "xl",
                        "weight": "bold",
                        "color": c["primary"]
                    },
                    {
                        "type": "separator",
                        "margin": "md",
                        "color": c["border"]
                    },
                    {
                        "type": "text",
                        "text": "الأوامر الأساسية:",
                        "size": "md",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "lg"
                    },
                    {
                        "type": "text",
                        "text": "بداية - القائمة الرئيسية\nالعاب - قائمة الألعاب\nثيم - تغيير الثيم",
                        "size": "sm",
                        "color": c["text_secondary"],
                        "wrap": True,
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": "أوامر المجموعات:",
                        "size": "md",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "تسجيل - الانضمام للعبة\nانسحاب - الخروج من اللعبة\nبدء - بدء اللعبة\nايقاف - إيقاف اللعبة\nنقاط - عرض النقاط\nلاعبين - قائمة اللاعبين",
                        "size": "sm",
                        "color": c["text_secondary"],
                        "wrap": True,
                        "margin": "sm"
                    },
                    {
                        "type": "text",
                        "text": "أوامر أخرى:",
                        "size": "md",
                        "weight": "bold",
                        "color": c["text"],
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "تحدي - تحديات عشوائية\nاعتراف - اعترافات\nسؤال - أسئلة عامة\nحكمه - حكم وأقوال\nموقف - مواقف افتراضية",
                        "size": "sm",
                        "color": c["text_secondary"],
                        "wrap": True,
                        "margin": "sm"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
    
    def _cmd_register(self, user_id, group_id, display_name, theme):
        if db.is_player_registered(group_id, user_id):
            return []
        
        session = db.get_session(group_id)
        if not session:
            return [TextMessage(text=MESSAGES['need_game'])]
        
        if db.add_player(group_id, user_id, display_name):
            count = len(session.players)
            return [TextMessage(text=f"{display_name} {MESSAGES['registration_success']}\nعدد اللاعبين: {count}")]
        
        return []
    
    def _cmd_leave(self, user_id, group_id, display_name, theme):
        if db.is_player_registered(group_id, user_id):
            db.remove_player(group_id, user_id)
            return [TextMessage(text=f"{display_name} انسحب من اللعبة")]
        return []
    
    def _cmd_select_game(self, group_id, game_name, theme):
        if not game_loader.game_exists(game_name):
            return [TextMessage(text=MESSAGES['game_not_found'])]
        
        session = db.get_session(group_id)
        if session and session.is_active:
            return [TextMessage(text=MESSAGES['already_active'])]
        
        db.create_session(group_id, game_name)
        game = game_loader.get_game(game_name)
        
        c = Config.THEMES[theme]
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": game.name,
                        "size": "xl",
                        "weight": "bold",
                        "color": c["primary"]
                    },
                    {
                        "type": "text",
                        "text": game.description,
                        "size": "md",
                        "color": c["text"],
                        "wrap": True,
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"عدد اللاعبين: {game.min_players}-{game.max_players}",
                        "size": "sm",
                        "color": c["text_secondary"],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "انضم", "text": "تسجيل"},
                                "style": "primary",
                                "color": c["success"],
                                "flex": 1
                            },
                            {
                                "type": "button",
                                "action": {"type": "message", "label": "بدء", "text": "بدء"},
                                "style": "primary",
                                "color": c["primary"],
                                "flex": 1
                            }
                        ],
                        "spacing": "sm",
                        "margin": "lg"
                    }
                ],
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
        
        return [FlexMessage(alt_text=game.name, contents=bubble)]
    
    def _cmd_start_game(self, group_id, theme):
        session = db.get_session(group_id)
        
        if not session:
            return [TextMessage(text=MESSAGES['need_game'])]
        
        if session.is_active:
            return [TextMessage(text=MESSAGES['already_active'])]
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return [TextMessage(text=MESSAGES['game_not_found'])]
        
        player_count = len(session.players)
        if player_count < game.min_players:
            return [TextMessage(text=f"{MESSAGES['min_players']}\nالعدد المطلوب: {game.min_players}\nالعدد الحالي: {player_count}")]
        
        success, message = game.start(group_id, session.players)
        
        if success:
            session.is_active = True
        
        return [TextMessage(text=message)]
    
    def _cmd_end_game(self, group_id, theme):
        session = db.get_session(group_id)
        
        if not session or not session.is_active:
            return [TextMessage(text=MESSAGES['no_active_game'])]
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return [TextMessage(text=MESSAGES['game_not_found'])]
        
        success, message = game.end(group_id)
        
        if success:
            session.is_active = False
        
        return [TextMessage(text=message)]
    
    def _cmd_scoreboard(self, group_id, theme):
        session = db.get_session(group_id)
        
        if not session:
            return [TextMessage(text="لا توجد لعبة")]
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return [TextMessage(text=MESSAGES['game_not_found'])]
        
        message = game.get_status(group_id)
        return [TextMessage(text=message)]
    
    def _cmd_list_players(self, group_id, theme):
        session = db.get_session(group_id)
        
        if not session or not session.players:
            return [TextMessage(text="لا يوجد لاعبون")]
        
        c = Config.THEMES[theme]
        contents = [
            {
                "type": "text",
                "text": "اللاعبون المسجلون",
                "size": "xl",
                "weight": "bold",
                "color": c["primary"]
            },
            {
                "type": "separator",
                "margin": "md",
                "color": c["border"]
            }
        ]
        
        for i, player in enumerate(session.players.values(), 1):
            contents.append({
                "type": "text",
                "text": f"{i}. {player.display_name}",
                "size": "md",
                "color": c["text"],
                "margin": "sm"
            })
        
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
                "backgroundColor": c["bg"],
                "paddingAll": "20px"
            }
        }
        
        return [FlexMessage(alt_text="اللاعبون", contents=bubble)]
    
    def _handle_game_message(self, group_id, user_id, text, theme):
        session = db.get_session(group_id)
        
        if not session or not session.is_active:
            return []
        
        game = game_loader.get_game(session.game_name)
        if not game:
            return []
        
        response, should_reply = game.process_message(group_id, user_id, text)
        
        if should_reply and response:
            return [TextMessage(text=response)]
        
        return []
