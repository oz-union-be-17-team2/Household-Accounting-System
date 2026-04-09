from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
# Transaction 모델을 admin page에 등록하는 데코레이터(장고의 어드민 페이지에 거래내역칸을 등록)
# 이게 없으면 어드민 페이지에서 Transaction 데이터를 볼 수 없다.
# 동일한 방식으로는 admin.site.register()로 직접 로직안에서 구현하는 방법도 있지만
# 데코레이터 방식이 더 직관적이고 코드를 줄일 수 있어서 사용하였습니다.
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "account", "transaction_type", "amount", "created_at"]
    # display를 사용하는 목적은 admin page에서 테이블 컬럼으로 표시할 필드를 지정해서
    # 사용자가 목록에서 한 눈에 보기 편하게 하기 위해서 사용
    # 과제를 반영해서 표시할 필드 지정
    search_fields = ["user__nickname", "description"]
    # 해당 유저의 닉네임과 해당거래내역에 비고부분을 admin page에서 검색해서 찾기
    list_filter = ["transaction_type"]
    # 검색 시에 필터 즉 사용자가 거래 타입(입금, 출금)등을 선택할 수 있게 설계
