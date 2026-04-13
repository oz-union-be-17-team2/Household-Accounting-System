from rest_framework.exceptions import APIException


class NotificationNotFoundError(APIException):
    status_code = 404
    default_detail = "알림을 찾을 수 없습니다."
