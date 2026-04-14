from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.notification.selectors import get_notification_detail, get_notification_list
from app.notification.serializers import NotificationSerializer
from app.notification.services import (
    delete_notification,
    mark_notification_as_read,
)


class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="알림 목록 조회",
        description="알림 목록을 조회합니다.",
        responses={200: NotificationSerializer},
    )
    def get(self, request):
        notification_list = get_notification_list(user=request.user)
        serializer = NotificationSerializer(notification_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="알림 디테일 조회",
        description="알림 조회 및 읽은 표시",
        responses={200: NotificationSerializer},
    )
    def get(self, request, noti_pk):
        notification = get_notification_detail(user=request.user, noti_pk=noti_pk)
        mark_notification_as_read(notification)
        serializer = NotificationSerializer(notification, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="알림 디테일 삭제",
        description="조회한 알림 수동 삭제",
        responses={204: None},
    )
    def delete(self, request, noti_pk):
        notification = get_notification_detail(user=request.user, noti_pk=noti_pk)
        delete_notification(notification)
        return Response(status=status.HTTP_204_NO_CONTENT)
