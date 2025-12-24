import random
import os
import logging

logger = logging.getLogger(__name__)

class TextManager:
    def __init__(self, base_path="games"):
        self.base_path = base_path
        # كل أمر مرتبط بملف واحد فقط لتجنب التكرار
        self.files = {
            "تحدي": "challenges.txt",
            "اعتراف": "confessions.txt",
            "منشن": "mentions.txt",
            "شخصية": "personality.txt",
            "سؤال": "questions.txt",
            "حكمة": "quotes.txt",
            "موقف": "situations.txt"
        }
        self.data = {}
        self._load_all()

    def _load_all(self):
        for cmd, filename in self.files.items():
            path = os.path.join(self.base_path, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                    self.data[cmd] = lines if lines else [f"المحتوى غير متوفر: {filename}"]
            except Exception as e:
                self.data[cmd] = [f"خطأ في تحميل {filename}"]
                logger.error(f"TextManager: failed to load {filename} - {e}")

    def get_content(self, cmd: str) -> str:
        """إرجاع محتوى عشوائي للأمر، أو رسالة افتراضية إذا لم يتوفر"""
        content_list = self.data.get(cmd)
        if content_list:
            return random.choice(content_list)
        return "المحتوى غير متوفر لهذا الأمر"

# نسخة جاهزة للاستخدام
text_manager = TextManager()
