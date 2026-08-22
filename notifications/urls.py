from django.urls import path
from .views import NotificationListView, NotificationReadView, NotificationPreferenceView, RegisterDeviceTokenView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('read/', NotificationReadView.as_view(), name='notification-read'),
    path('preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('register-device/', RegisterDeviceTokenView.as_view(), name='register-device'),
]
