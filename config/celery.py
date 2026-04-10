import os

from celery import Celery

# Django 설정 파일 위치 알려주기
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.setting.base")

# Celery 앱 인스턴스 생성
app = Celery("household_accounting")

# base.py에서 CELERY_로 시작하는 설정을 자동으로 읽어옴
app.config_from_object("django.conf:settings", namespace="CELERY")

# 각 앱의 tasks.py를 자동으로 찾아서 등록
app.autodiscover_tasks()
