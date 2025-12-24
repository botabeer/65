from functools import wraps
from database import db
from config import OWNER_USER_ID, SECURITY_SETTINGS, MESSAGES
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.enabled = SECURITY_SETTINGS['enable_spam_protection']
        self.max_messages = SECURITY_SETTINGS['max_messages_per_minute']
        self.ban_duration = SECURITY_SETTINGS['ban_duration']
        self.auto_ban_warnings = SECURITY_SETTINGS['auto_ban_after_warnings']
        
        logger.info(f"Security initialized - Spam protection: {self.enabled}")
    
    def check_spam(self, user_id: str) -> tuple[bool, Optional[str]]:
        if not self.enabled:
            return True, None
        
        if user_id == OWNER_USER_ID or db.is_admin(user_id):
            return True, None
        
        if db.is_banned(user_id):
            logger.warning(f"Banned user attempted access: {user_id}")
            return False, MESSAGES['banned']
        
        message_count = db.record_message(user_id)
        
        if message_count > self.max_messages:
            warnings = db.add_warning(user_id)
            logger.warning(f"User {user_id} exceeded rate limit: {message_count} msgs, {warnings} warnings")
            
            if warnings >= self.auto_ban_warnings:
                db.ban_user(user_id, self.ban_duration)
                logger.info(f"Auto-banned user {user_id} after {warnings} warnings")
                return False, MESSAGES['banned']
            
            return False, MESSAGES['spam_warning']
        
        return True, None
    
    def is_owner(self, user_id: str) -> bool:
        return user_id == OWNER_USER_ID
    
    def is_authorized(self, user_id: str) -> bool:
        return self.is_owner(user_id) or db.is_admin(user_id)
    
    def sanitize_input(self, text: str) -> str:
        if not text:
            return ""
        
        text = text.strip()
        text = text.replace('\x00', '')
        text = ' '.join(text.split())
        
        if len(text) > 2000:
            text = text[:2000]
        
        return text
    
    def validate_command(self, text: str) -> bool:
        if not text or not text.startswith('/'):
            return False
        
        if len(text) > 500:
            return False
        
        return True

security = SecurityManager()

def owner_only(func):
    @wraps(func)
    def wrapper(event, *args, **kwargs):
        user_id = event.source.user_id
        if not security.is_owner(user_id):
            logger.warning(f"Unauthorized owner command attempt by {user_id}")
            return None
        return func(event, *args, **kwargs)
    return wrapper

def admin_only(func):
    @wraps(func)
    def wrapper(event, *args, **kwargs):
        user_id = event.source.user_id
        if not security.is_authorized(user_id):
            logger.warning(f"Unauthorized admin command attempt by {user_id}")
            return None
        return func(event, *args, **kwargs)
    return wrapper

def registered_only(func):
    @wraps(func)
    def wrapper(event, *args, **kwargs):
        user_id = event.source.user_id
        group_id = getattr(event.source, 'group_id', None)
        
        if not group_id or not db.is_player_registered(group_id, user_id):
            return None
        
        return func(event, *args, **kwargs)
    return wrapper
