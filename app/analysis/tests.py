import os
from datetime import date

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from app.account.models import Account
from app.analysis.analyzer import SpendingAnalyzer
from app.analysis.models import Analysis
from app.transaction.models import Transaction

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@test.com",
        password="test1234!",
        nickname="테스터",
        gender="M",
        age=20,
        job="개발자",
    )


@pytest.fixture
def account(db, user):
    return Account.objects.create(
        user=user,
        name="테스트통장",
        number="1234567890",
        account_type=Account.AccountType.CHECKING,
        bank_code=Account.BankCode.KB,
    )


@pytest.fixture
def transaction(db, user, account):
    return Transaction.objects.create(
        user=user,
        account=account,
        amount=50000,
        transaction_type=Transaction.TransactionType.WITHDRAWAL,
    )


@pytest.fixture
def analysis(db, user):
    return Analysis.objects.create(
        user=user,
        about="총 지출",
        analysis_type=Analysis.AnalysisType.WEEKLY,
        period_start=date(2026, 4, 1),
        period_end=date(2026, 4, 7),
        description="테스트 분석",
    )


@pytest.fixture
def client():
    return APIClient()


# 인증된 유저 - 분석 결과 목록 조회
@pytest.mark.django_db
def test_analysis_list(client, user, analysis):
    client.force_authenticate(user=user)
    response = client.get("/analysis/")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


# 인증된 유저 - WEEKLY 필터 조회
@pytest.mark.django_db
def test_analysis_list_filter_weekly(client, user, analysis):
    client.force_authenticate(user=user)
    response = client.get("/analysis/?analysis_type=WEEKLY")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


# 인증된 유저 - MONTHLY 필터 조회 (결과 없음)
@pytest.mark.django_db
def test_analysis_list_filter_monthly(client, user, analysis):
    client.force_authenticate(user=user)
    response = client.get("/analysis/?analysis_type=MONTHLY")
    assert response.status_code == 200
    assert len(response.data["results"]) == 0


# 인증되지 않은 유저 - 401 반환
@pytest.mark.django_db
def test_analysis_list_unauthenticated(client, analysis):
    response = client.get("/analysis/")
    assert response.status_code == 401


# 다른 유저의 분석 결과는 조회 안 됨
@pytest.mark.django_db
def test_analysis_list_other_user(client, analysis):
    other_user = User.objects.create_user(
        email="other@test.com",
        password="test1234!",
        nickname="다른유저",
        gender="M",
        age=20,
        job="개발자",
    )
    client.force_authenticate(user=other_user)
    response = client.get("/analysis/")
    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_fetch_data(user, transaction):
    # 거래내역을 올바르게 가져오는지 확인
    analyzer = SpendingAnalyzer(
        user=user,
        period_start=date(2024, 1, 1),
        period_end=date(2099, 12, 31),
        analysis_type=Analysis.AnalysisType.WEEKLY,
    )
    analyzer.fetch_data()

    assert analyzer.df is not None
    assert len(analyzer.df) == 1


@pytest.mark.django_db
def test_fetch_data_no_transactions(user):
    # 거래내역 없을 때 ValueError 발생하는지 확인
    analyzer = SpendingAnalyzer(
        user=user,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 7),
        analysis_type=Analysis.AnalysisType.WEEKLY,
    )

    with pytest.raises(ValueError):
        analyzer.fetch_data()


@pytest.mark.django_db
def test_analyze(user, transaction):
    # DataFrame이 올바르게 가공되는지 확인
    analyzer = SpendingAnalyzer(
        user=user,
        period_start=date(2024, 1, 1),
        period_end=date(2099, 12, 31),
        analysis_type=Analysis.AnalysisType.WEEKLY,
    )
    analyzer.fetch_data()
    analyzer.analyze()

    assert "date" in analyzer.df.columns
    assert "amount" in analyzer.df.columns
    assert analyzer.df["amount"].sum() == 50000.0


@pytest.mark.django_db
def test_visualize(user, transaction, tmp_path, settings):
    # 이미지 파일이 생성되는지 확인
    settings.MEDIA_ROOT = tmp_path  # 테스트용 임시 경로 사용

    analyzer = SpendingAnalyzer(
        user=user,
        period_start=date(2024, 1, 1),
        period_end=date(2099, 12, 31),
        analysis_type=Analysis.AnalysisType.WEEKLY,
    )
    analyzer.fetch_data()
    analyzer.analyze()
    analyzer.visualize()

    assert analyzer.image_path is not None
    assert os.path.exists(os.path.join(tmp_path, analyzer.image_path))


@pytest.mark.django_db
def test_save(user, transaction, tmp_path, settings):
    # Analysis 모델이 올바르게 생성되는지 확인
    settings.MEDIA_ROOT = tmp_path

    analyzer = SpendingAnalyzer(
        user=user,
        period_start=date(2024, 1, 1),
        period_end=date(2099, 12, 31),
        analysis_type=Analysis.AnalysisType.WEEKLY,
    )
    analyzer.fetch_data()
    analyzer.analyze()
    analyzer.visualize()
    analyzer.save()

    assert Analysis.objects.count() == 1
    analysis = Analysis.objects.first()
    assert analysis.user == user
    assert analysis.about == "총 지출"
    assert analysis.analysis_type == Analysis.AnalysisType.WEEKLY


@pytest.mark.django_db
def test_run(user, transaction, tmp_path, settings):
    # 전체 흐름이 올바르게 동작하는지 확인
    settings.MEDIA_ROOT = tmp_path

    analyzer = SpendingAnalyzer(
        user=user,
        period_start=date(2024, 1, 1),
        period_end=date(2099, 12, 31),
        analysis_type=Analysis.AnalysisType.WEEKLY,
    )
    analyzer.run()

    assert Analysis.objects.count() == 1
    assert analyzer.df is not None
    assert analyzer.image_path is not None
