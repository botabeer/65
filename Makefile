.PHONY: help install run dev docker-build docker-run docker-stop clean test

help:
	@echo "Bot Mesh - أوامر مساعدة"
	@echo ""
	@echo "make install       - تثبيت المكتبات"
	@echo "make run          - تشغيل التطبيق (إنتاج)"
	@echo "make dev          - تشغيل التطبيق (تطوير)"
	@echo "make docker-build - بناء Docker image"
	@echo "make docker-run   - تشغيل Docker container"
	@echo "make docker-stop  - إيقاف Docker container"
	@echo "make clean        - تنظيف الملفات المؤقتة"
	@echo "make test         - اختبار الألعاب"

install:
	pip install -r requirements.txt

run:
	gunicorn -c gunicorn_config.py app:app

dev:
	python app.py

docker-build:
	docker build -t botmesh .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db-shm" -delete
	find . -type f -name "*.db-wal" -delete

test:
	python -c "from games.iq import IQGame; from database import Database; db = Database(); game = IQGame(db); print('✓ IQ Game OK')"
	python -c "from games.math import MathGame; from database import Database; db = Database(); game = MathGame(db); print('✓ Math Game OK')"
	python -c "from games.guess import GuessGame; from database import Database; db = Database(); game = GuessGame(db); print('✓ Guess Game OK')"
	@echo "✓ جميع الألعاب تعمل بشكل صحيح"
