from django.urls import path

from app.notification.views import NotificationDetailAPIView, NotificationListAPIView

app_name = "notification"


urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="list"),
    path("<int:noti_pk>/", NotificationDetailAPIView.as_view(), name="detail"),
]
