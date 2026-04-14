import os
from datetime import datetime, time

import matplotlib

matplotlib.use("Agg")  # GUI 없이 이미지 파일로만 저장 (웹서버/스레드 환경)
import matplotlib.pyplot as plt
import pandas as pd
from django.conf import settings
from django.utils import timezone

from app.transaction.models import Transaction

from .models import Analysis

# Matplotlib 한글 폰트 설정
# NanumGothic: Linux 서버(Docker)에서 사용 가능한 한글 폰트
# AppleGothic은 macOS 전용이라 서버에서 사용 불가
plt.rcParams["font.family"] = "NanumGothic"
# 한글 폰트로 바꾸면 -기호가 깨지는 문제가 발생하는데 그것을 방지하는 설정이다
plt.rcParams["axes.unicode_minus"] = False


class SpendingAnalyzer:
    def __init__(self, user, period_start, period_end, analysis_type):
        self.user = user
        self.period_start = period_start
        self.period_end = period_end
        self.df = None
        self.image_path = None
        self.analysis_type = analysis_type

    def fetch_data(self):
        transactions = Transaction.objects.filter(
            user=self.user,
            transaction_type="WITHDRAWAL",
            created_at__range=(
                timezone.make_aware(datetime.combine(self.period_start, time.min)),
                timezone.make_aware(datetime.combine(self.period_end, time.max)),
            ),
        ).select_related("account")

        if not transactions.exists():
            raise ValueError("분석할 거래내역이 없습니다.")

        self.df = pd.DataFrame(list(transactions.values("amount", "created_at")))

    def analyze(self):
        self.df["date"] = pd.to_datetime(self.df["created_at"]).dt.date
        self.df["amount"] = self.df["amount"].astype(float)
        self.df = self.df.groupby("date")["amount"].sum().reset_index()

    def visualize(self):
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(self.df["date"].astype(str), self.df["amount"])
        ax.set_title("기간별 지출 분석")
        ax.set_xlabel("날짜")
        ax.set_ylabel("지출 금액 (원)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        save_dir = os.path.join(settings.MEDIA_ROOT, "analysis")
        os.makedirs(save_dir, exist_ok=True)

        filename = f"analysis_{self.user.id}_{self.period_start}_{self.period_end}.png"
        self.image_path = os.path.join("analysis", filename)

        plt.savefig(os.path.join(settings.MEDIA_ROOT, self.image_path))
        plt.close()

    def save(self):
        Analysis.objects.create(
            user=self.user,
            about="총 지출",
            analysis_type=self.analysis_type,
            period_start=self.period_start,
            period_end=self.period_end,
            description=f"{self.period_start} ~ {self.period_end} 기간 총 지출: {self.df['amount'].sum():,.0f}원",
            result_image=self.image_path,
        )

    def run(self):
        self.fetch_data()
        self.analyze()
        self.visualize()
        self.save()
