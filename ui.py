"""
Bot 65 - UI Module
Fixed Dark Theme
"""

class UI:
    THEMES = {
        'light': {
            'p':'#2563EB', 's':'#10B981', 'w':'#F59E0B', 'e':'#EF4444',
            't':'#1F2937', 't2':'#6B7280', 'bg':'#FFFFFF', 'bg2':'#F3F4F6', 'b':'#E5E7EB'
        },
        'dark': {
            'p':'#60A5FA', 's':'#4ADE80', 'w':'#FBBF24', 'e':'#F87171',
            't':'#F1F5F9', 't2':'#94A3B8', 'bg':'#0F172A', 'bg2':'#1E293B', 'b':'#334155'
        }
    }
    
    @staticmethod
    def _c(theme):
        return UI.THEMES.get(theme, UI.THEMES['light'])
    
    @staticmethod
    def welcome(name, registered, theme='light'):
        c = UI._c(theme)
        status = "مسجل" if registered else "غير مسجل"
        status_color = c['s'] if registered else c['w']
        return {
            "type":"bubble",
            "body":{
                "type":"box",
                "layout":"vertical",
                "contents":[
                    {"type":"text","text":"Bot 65","weight":"bold","size":"xxl","color":c['p'],"align":"center"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    {"type":"text","text":f"مرحبا {name}","size":"lg","color":c['t'],"align":"center","margin":"lg"},
                    {"type":"text","text":status,"size":"sm","color":status_color,"align":"center","margin":"md"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"العاب","text":"العاب"},"style":"primary","color":c['p'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"نقاطي","text":"نقاطي"},"style":"primary","color":c['p'],"height":"sm"}
                    ],"spacing":"sm","margin":"lg"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"الصدارة","text":"الصدارة"},"style":"secondary","height":"sm"},
                        {"type":"button","action":{"type":"message","label":"مساعدة","text":"مساعدة"},"style":"secondary","height":"sm"}
                    ],"spacing":"sm","margin":"sm"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    {"type":"text","text":"للتسجيل: تسجيل","size":"xs","color":c['t2'],"align":"center","margin":"md"}
                ],
                "paddingAll":"20px"
            }
        }
    
    @staticmethod
    def games_menu(theme='light'):
        c = UI._c(theme)
        return {
            "type":"bubble",
            "body":{
                "type":"box",
                "layout":"vertical",
                "contents":[
                    {"type":"text","text":"قائمة الألعاب","weight":"bold","size":"xl","color":c['p'],"align":"center"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    {"type":"text","text":"العاب تنافسية","size":"md","color":c['t'],"weight":"bold","margin":"lg"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"اغنية","text":"اغنيه"},"style":"primary","color":c['p'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"اضداد","text":"ضد"},"style":"primary","color":c['p'],"height":"sm"}
                    ],"spacing":"sm","margin":"md"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"سلسلة","text":"سلسله"},"style":"primary","color":c['p'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"كتابة","text":"اسرع"},"style":"primary","color":c['p'],"height":"sm"}
                    ],"spacing":"sm","margin":"sm"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"تكوين","text":"تكوين"},"style":"primary","color":c['p'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"فئة","text":"فئه"},"style":"primary","color":c['p'],"height":"sm"}
                    ],"spacing":"sm","margin":"sm"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"ذكاء","text":"ذكاء"},"style":"primary","color":c['p'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"خمن","text":"خمن"},"style":"primary","color":c['p'],"height":"sm"}
                    ],"spacing":"sm","margin":"sm"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"ترتيب","text":"ترتيب"},"style":"primary","color":c['p'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"لون","text":"لون"},"style":"primary","color":c['p'],"height":"sm"}
                    ],"spacing":"sm","margin":"sm"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"روليت","text":"روليت"},"style":"primary","color":c['p'],"height":"sm"},
                        {"type":"button","action":{"type":"message","label":"سين جيم","text":"سين"},"style":"primary","color":c['p'],"height":"sm"}
                    ],"spacing":"sm","margin":"sm"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    {"type":"text","text":"العاب جماعية","size":"md","color":c['t'],"weight":"bold","margin":"md"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"لعبة","text":"لعبه"},"style":"secondary","height":"sm"},
                        {"type":"button","action":{"type":"message","label":"حروف","text":"حروف"},"style":"secondary","height":"sm"}
                    ],"spacing":"sm","margin":"md"},
                    {"type":"box","layout":"horizontal","contents":[
                        {"type":"button","action":{"type":"message","label":"توافق","text":"توافق"},"style":"secondary","height":"sm","color":c['w']},
                        {"type":"button","action":{"type":"message","label":"مافيا","text":"مافيا"},"style":"secondary","height":"sm","color":c['e']}
                    ],"spacing":"sm","margin":"sm"}
                ],
                "paddingAll":"20px"
            }
        }
    
    @staticmethod
    def help_card(theme='light'):
        c = UI._c(theme)
        return {
            "type":"bubble",
            "body":{
                "type":"box",
                "layout":"vertical",
                "contents":[
                    {"type":"text","text":"دليل الاستخدام","weight":"bold","size":"xl","color":c['p'],"align":"center"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    UI._section("الأوامر الأساسية", "بداية - العاب - نقاطي - الصدارة - تسجيل - ثيم", c),
                    {"type":"separator","margin":"md","color":c['b']},
                    UI._section("أوامر نصية", "سؤال - تحدي - اعتراف - منشن - حكمة - موقف", c),
                    {"type":"separator","margin":"md","color":c['b']},
                    UI._section("الألعاب الفردية", "اغنيه - ضد - سلسله - اسرع - تكوين - فئه - ذكاء - خمن - ترتيب - لون - روليت - سين", c),
                    {"type":"separator","margin":"md","color":c['b']},
                    UI._section("الألعاب الجماعية", "لعبه - حروف - توافق - مافيا", c),
                    {"type":"separator","margin":"md","color":c['b']},
                    UI._section("أثناء اللعب", "لمح: تلميح | جاوب: عرض الاجابة | انسحب: الخروج من اللعبة", c)
                ],
                "paddingAll":"20px"
            }
        }
    
    @staticmethod
    def stats(user, theme='light'):
        c = UI._c(theme)
        rate = round((user['wins'] / user['games'] * 100) if user['games'] > 0 else 0)
        return {
            "type":"bubble",
            "body":{
                "type":"box",
                "layout":"vertical",
                "contents":[
                    {"type":"text","text":"احصائياتك","weight":"bold","size":"xl","color":c['p'],"align":"center"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    {"type":"text","text":user['name'],"size":"xl","color":c['t'],"align":"center","weight":"bold","margin":"lg"},
                    {"type":"separator","margin":"lg","color":c['b']},
                    UI._stat("النقاط", str(user['points']), c),
                    UI._stat("الألعاب", str(user['games']), c),
                    UI._stat("الفوز", str(user['wins']), c),
                    UI._stat("نسبة الفوز", f"{rate}%", c)
                ],
                "paddingAll":"20px"
            }
        }
    
    @staticmethod
    def leaderboard(leaders, theme='light'):
        c = UI._c(theme)
        contents = [
            {"type":"text","text":"لوحة الصدارة","weight":"bold","size":"xl","color":c['p'],"align":"center"},
            {"type":"separator","margin":"lg","color":c['b']}
        ]
        if not leaders:
            contents.append({"type":"text","text":"لا توجد بيانات","size":"sm","color":c['t2'],"align":"center","margin":"lg"})
        else:
            for i, leader in enumerate(leaders[:20], 1):
                contents.append(UI._leader(str(i), leader['name'], str(leader['points']), c))
        return {
            "type":"bubble",
            "body":{
                "type":"box",
                "layout":"vertical",
                "contents":contents,
                "paddingAll":"20px"
            }
        }
    
    @staticmethod
    def _section(title, content, c):
        return {
            "type":"box",
            "layout":"vertical",
            "contents":[
                {"type":"text","text":title,"weight":"bold","size":"sm","color":c['p']},
                {"type":"text","text":content,"size":"xs","color":c['t2'],"wrap":True,"margin":"xs"}
            ],
            "margin":"md"
        }
    
    @staticmethod
    def _stat(label, value, c):
        return {
            "type":"box",
            "layout":"baseline",
            "contents":[
                {"type":"text","text":label,"size":"sm","color":c['t2'],"flex":3},
                {"type":"text","text":value,"size":"lg","weight":"bold","color":c['p'],"align":"end","flex":2}
            ],
            "margin":"md"
        }
    
    @staticmethod
    def _leader(rank, name, points, c):
        medals = {"1":"🥇","2":"🥈","3":"🥉"}
        rank_text = medals.get(rank, rank + ".")
        return {
            "type":"box",
            "layout":"baseline",
            "contents":[
                {"type":"text","text":rank_text,"size":"sm","color":c['p'] if rank in medals else c['t2'],"flex":0,"weight":"bold"},
                {"type":"text","text":name,"size":"sm","color":c['t'],"flex":4,"margin":"sm"},
                {"type":"text","text":points,"size":"sm","weight":"bold","color":c['s'],"align":"end","flex":1}
            ],
            "margin":"sm",
            "paddingAll":"8px"
        }
