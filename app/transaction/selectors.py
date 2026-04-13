from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from app.transaction.models import Transaction

User = get_user_model()


def get_transaction_list(
    *, user: User, transaction_type=None, amount_min=None, amount_max=None
) -> QuerySet[Transaction]:
    transaction = Transaction.objects.filter(user=user).select_related("account")
    # (transaction)N -> 1(account)관계에서 select_related()로
    # 전체를 JOIN해서 가져와서 N+1 문제를 해결
    # 그냥 필터링으로 조회하게 돼면 쿼리 발생 시 해당 부분을 DB에서 전체를
    # 한번씩 조회 후 해당 부분을 가져오기에 N+1문제 발생
    # 그냥 필터링을 DB에서 조회하지않고 select_related()로 가져와서 메모리에서 찾음
    # self.request.user을 통해 해당유저의 거래내역을 가져오고
    # select_related()를 사용해서 계좌와 거래내역을 조인해서 가져온다

    if transaction_type:
        transaction = transaction.filter(transaction_type=transaction_type)
    if amount_min:
        transaction = transaction.filter(amount__gte=amount_min)
    if amount_max:
        transaction = transaction.filter(amount__lte=amount_max)
    return transaction
