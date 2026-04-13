from rest_framework import serializers

from app.notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",  # test 및 시연을 위해 생성
            "message",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",  # test 및 시연을 위해 생성
            "message",
            "is_read",
            "created_at",
        ]
