# 레이어 분리 (역할 분담)

fastapi에서 사용하던걸 비교해보자면
`repositories`는 db에서 꺼내거나 저장하는 역할을 수행한다.
레포와 비슷한 역할을 수행하는 건 `selectors`를 사용하고 꺼내는 역할을 수행한다
저장은 `views`에서 serializer.save()같은 형식으로 하거나

```python
# services
def abc_create(user):
    account = Account.objects.create(user=user)
    # 추가 비지니스 로직
    return account
```

```python
# views
class AbcAPIView(APIView)
    def post(self, request):
        serializer = AbcSerializer(data=request.data)
        if serializer.is_valid()
            abc = abc_create(
                user=request.user,
                **serializer.validated_data, #검증된 데이터를 서비스로 넘기기 위해 사용
            )
            return Response(AbcSerializer(abc).data, status=201)

```
위와 같은 형식으로 저장하기에 selectors를 사용함

`views`에서는 간단하게 if나 try n except로 없을 때만 체크해주고
다른 비지니스 로직은 `services`에서 처리

## selectors 작성 요령
```python
def abc(*, user):
    return Abc.objects.filter(user=user)
```
### *을 넣는 이유

1. *을 넣지 않았을 때는
abc(request.user) 사용 가능
abc(user=request.user) 사용 가능

2. *이 있을 때는
abc(request.user) 불가능
abc(user=request.user) 사용 가능

여러 인자를 받는 경우 1번의 경우에는 순서를 바꿔 넣어도 실행이 돼 오류가 발생
2번의 경우 항상 매칭시켜서 넣어야하기에 실수를 방지할 수 있다.
