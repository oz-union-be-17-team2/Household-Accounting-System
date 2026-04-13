# 에러 처리 (핸들링 전)

exceptions.py는 에러를 명시적으로 남기기 위해서 작성

어떤 에러인지 클래스로 작성하고 Exception을 상속받는다

```python
# exceptions.py
class AccountNotFoundError(Exception):
    pass
```

```python
# selectors
def get_account_detail(*, user: User, account_pk: int) -> Account:
    try:
        return Account.objects.select_related('user').get(user=user, pk=account_pk)
    except Account.DoesNotExist:
        raise AccountNotFoundError("계좌를 찾을 수 없습니다.")
```

```python
# views
def get(self, request, account_pk):
    try:
        account = get_account_detail(user=request.user, account_pk=account_pk)
    except AccountNotFoundError as e:
        return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
```

겟으로 했을 때 없을 때 에러가 발생하기 때문에 사용했고 그외 에러 상황이 발생할 수 있을 때 비슷한 방식으로 사용할 수 있음
Exception 상속받기에 내부에 작성한 메시지가 반환된다
명시적으로 표시하기 위해 클래스를 작성해서 사용

추가적으로 get이 아니라 filter.first를 사용했을 때는 try except 대신 if에서 raise AccountNotFoundError()로 처리하면 동일
