# 에러 핸들링

기본적으로 에러 핸들링을 위해선
settings에 추가 필요
```
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}
```

core/exceptions.py 에서 작성한 핸들링으로 내용을 수정할 수 있음
```python
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "status_code": response.status_code,
            "errors": response.data,
            "message": getattr(exc, "detail", "정의되지 않는 오류가 발생했습니다."),
        }
    return response
```

default_detail에 입력한 내용을 exc.detail로 호출할 수 있음
getattr를 사용한 이유는 message가 항상 있지 않기에 없을 경우 예외처리
