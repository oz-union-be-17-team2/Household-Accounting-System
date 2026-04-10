from rest_framework import status
from rest_framework.exceptions import APIException


class AccountNotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "계좌를 찾을 수 없습니다."
