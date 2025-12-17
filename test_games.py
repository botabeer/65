import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from games.iq import IQGame
from games.math import MathGame
from games.guess import GuessGame
from games.scramble import ScrambleGame
from games.opposite import OppositeGame
from config import Config

def test_database():
    print("اختبار قاعدة البيانات...")
    db = Database(":memory:")
    
    user_id = "test_user"
    db.register_user(user_id, "اختبار")
    user = db.get_user(user_id)
    
    assert user is not None
    assert user['name'] == "اختبار"
    assert user['points'] == 0
    
    db.add_points(user_id, 10)
    user = db.get_user(user_id)
    assert user['points'] == 10
    
    db.increment_games(user_id)
    user = db.get_user(user_id)
    assert user['games'] == 1
    
    db.increment_wins(user_id)
    user = db.get_user(user_id)
    assert user['wins'] == 1
    assert user['streak'] == 1
    
    print("✓ قاعدة البيانات تعمل بشكل صحيح")

def test_iq_game():
    print("اختبار لعبة الذكاء...")
    db = Database(":memory:")
    game = IQGame(db)
    
    question = game.start()
    assert question is not None
    assert game.current_q == 1
    assert game.score == 0
    
    print("✓ لعبة الذكاء تعمل بشكل صحيح")

def test_math_game():
    print("اختبار لعبة الرياضيات...")
    db = Database(":memory:")
    game = MathGame(db)
    
    question = game.start()
    assert question is not None
    assert game.current_answer is not None
    
    print("✓ لعبة الرياضيات تعمل بشكل صحيح")

def test_guess_game():
    print("اختبار لعبة خمن...")
    db = Database(":memory:")
    game = GuessGame(db)
    
    question = game.start()
    assert question is not None
    assert len(game.current_answer) > 0
    
    print("✓ لعبة خمن تعمل بشكل صحيح")

def test_scramble_game():
    print("اختبار لعبة ترتيب الحروف...")
    db = Database(":memory:")
    game = ScrambleGame(db)
    
    question = game.start()
    assert question is not None
    assert game.current_answer is not None
    
    print("✓ لعبة ترتيب الحروف تعمل بشكل صحيح")

def test_opposite_game():
    print("اختبار لعبة الأضداد...")
    db = Database(":memory:")
    game = OppositeGame(db)
    
    question = game.start()
    assert question is not None
    assert len(game.current_answer) > 0
    
    print("✓ لعبة الأضداد تعمل بشكل صحيح")

def test_normalize():
    print("اختبار تطبيع النصوص...")
    
    assert Config.normalize("أَحْمَد") == "احمد"
    assert Config.normalize("إبراهيم") == "ابراهيم"
    assert Config.normalize("مُحَمَّد") == "محمد"
    assert Config.normalize("كتاب") == "كتاب"
    assert Config.normalize("قِطَّة") == "قطه"
    
    print("✓ تطبيع النصوص يعمل بشكل صحيح")

def test_achievements():
    print("اختبار نظام الإنجازات...")
    db = Database(":memory:")
    user_id = "test_user"
    db.register_user(user_id, "اختبار")
    
    db.increment_games(user_id)
    achievements = db.check_achievements(user_id)
    assert len(achievements) == 1
    assert achievements[0]['name'] == "اللعبة الأولى"
    
    user = db.get_user(user_id)
    assert user['points'] == 5
    
    print("✓ نظام الإنجازات يعمل بشكل صحيح")

def test_daily_reward():
    print("اختبار المكافآت اليومية...")
    db = Database(":memory:")
    user_id = "test_user"
    db.register_user(user_id, "اختبار")
    
    assert db.can_claim_reward(user_id) == True
    
    db.claim_reward(user_id)
    user = db.get_user(user_id)
    assert user['points'] == 10
    
    assert db.can_claim_reward(user_id) == False
    
    print("✓ المكافآت اليومية تعمل بشكل صحيح")

def test_streak():
    print("اختبار نظام السلاسل...")
    db = Database(":memory:")
    user_id = "test_user"
    db.register_user(user_id, "اختبار")
    
    db.increment_wins(user_id)
    user = db.get_user(user_id)
    assert user['streak'] == 1
    assert user['best_streak'] == 1
    
    db.increment_wins(user_id)
    user = db.get_user(user_id)
    assert user['streak'] == 2
    assert user['best_streak'] == 2
    
    db.reset_streak(user_id)
    user = db.get_user(user_id)
    assert user['streak'] == 0
    assert user['best_streak'] == 2
    
    print("✓ نظام السلاسل يعمل بشكل صحيح")

def run_all_tests():
    print("=" * 50)
    print("بدء الاختبارات...")
    print("=" * 50)
    
    try:
        test_database()
        test_iq_game()
        test_math_game()
        test_guess_game()
        test_scramble_game()
        test_opposite_game()
        test_normalize()
        test_achievements()
        test_daily_reward()
        test_streak()
        
        print("=" * 50)
        print("✓ جميع الاختبارات نجحت")
        print("=" * 50)
        return True
    except AssertionError as e:
        print(f"✗ فشل الاختبار: {e}")
        return False
    except Exception as e:
        print(f"✗ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
