from datetime import datetime, timedelta
from config import SYSTEM_SETTINGS, MESSAGES
import logging

logger = logging.getLogger(__name__)

def check_user_spam(user_id, db):
    """
    فحص السبام للمستخدم
    يتجاهل الرسائل الزائدة بصمت دون إرسال رسائل خطأ في القروب
    """
    
    if not SYSTEM_SETTINGS.get("enable_spam_protection", True):
        return False
    
    # التحقق من الحظر
    if db.is_banned(user_id):
        logger.warning(f"Blocked message from banned user: {user_id}")
        return True  # تجاهل الرسالة بصمت
    
    # فحص معدل الرسائل
    max_messages = SYSTEM_SETTINGS.get("max_messages_per_minute", 15)
    
    if db.is_rate_limited(user_id, limit=max_messages):
        # إضافة تحذير
        warnings = db.add_warning(user_id)
        
        # إذا وصل للحد الأقصى من التحذيرات، يتم الحظر
        max_warnings = SYSTEM_SETTINGS.get("auto_ban_after_warnings", 3)
        
        if warnings >= max_warnings:
            ban_duration = timedelta(
                hours=SYSTEM_SETTINGS.get("ban_duration_hours", 1)
            )
            db.ban_user(user_id, ban_duration)
            logger.warning(f"User {user_id} banned for {ban_duration}")
        
        return True  # تجاهل الرسالة بصمت
    
    return False


def is_admin(user_id, db):
    """التحقق من صلاحيات المشرف"""
    from config import OWNER_USER_ID
    
    if user_id == OWNER_USER_ID:
        return True
    
    return db.is_admin(user_id)


def can_start_game(group_id, db):
    """التحقق من إمكانية بدء لعبة جديدة"""
    session = db.get_session(group_id)
    
    if session and session.is_active:
        return False, "يوجد لعبة نشطة بالفعل"
    
    return True, None


def can_interact(user_id, db):
    """التحقق من إمكانية تفاعل المستخدم"""
    
    # التحقق من الحظر
    if db.is_banned(user_id):
        return False, MESSAGES["user_banned"]
    
    return True, None


def sanitize_input(text):
    """تنظيف وتأمين المدخلات"""
    if not text:
        return ""
    
    # إزالة الأحرف الخطرة
    dangerous_chars = ['<', '>', '{', '}', '[', ']', '\\', '|']
    
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # تحديد الطول الأقصى
    max_length = 500
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()


class RateLimiter:
    """مدير حد المعدل المتقدم"""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = 300  # 5 دقائق
        self.last_cleanup = datetime.now()
    
    def check_limit(self, user_id, max_requests=10, window_seconds=60):
        """التحقق من حد المعدل"""
        now = datetime.now()
        
        # تنظيف السجلات القديمة
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            self._cleanup_old_requests()
        
        # إنشاء أو جلب سجل المستخدم
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # إزالة الطلبات القديمة
        cutoff_time = now - timedelta(seconds=window_seconds)
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > cutoff_time
        ]
        
        # التحقق من الحد
        if len(self.requests[user_id]) >= max_requests:
            return False
        
        # إضافة الطلب الحالي
        self.requests[user_id].append(now)
        return True
    
    def _cleanup_old_requests(self):
        """تنظيف الطلبات القديمة لتوفير الذاكرة"""
        now = datetime.now()
        cutoff_time = now - timedelta(minutes=5)
        
        users_to_remove = []
        
        for user_id, requests in self.requests.items():
            # إزالة الطلبات القديمة
            self.requests[user_id] = [
                req_time for req_time in requests
                if req_time > cutoff_time
            ]
            
            # إزالة المستخدمين بدون طلبات
            if not self.requests[user_id]:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.requests[user_id]
        
        self.last_cleanup = now
        
        if users_to_remove:
            logger.info(f"Cleaned up {len(users_to_remove)} inactive users")


# مثيل عام لـ RateLimiter
rate_limiter = RateLimiter()
