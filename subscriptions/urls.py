from django.urls import path
from .views import (
    SubscriptionPlanListView,
    MySubscriptionView,
    SubscribeView,
    CancelSubscriptionView,
    SSLCommerzInitiateView,
    SSLCommerzSuccessView,
    SSLCommerzFailView,
    SSLCommerzCancelView,
)

urlpatterns = [
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    path('my-subscription/', MySubscriptionView.as_view(), name='my-subscription'),
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('sslcommerz/subscribe/', SSLCommerzInitiateView.as_view(), name='sslcommerz-subscribe'),
    path('sslcommerz/success/', SSLCommerzSuccessView.as_view(), name='sslcommerz-success'),
    path('sslcommerz/fail/', SSLCommerzFailView.as_view(), name='sslcommerz-fail'),
    path('sslcommerz/cancel/', SSLCommerzCancelView.as_view(), name='sslcommerz-cancel'),
    path('cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
]
