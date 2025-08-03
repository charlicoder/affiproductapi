from django.urls import path
from .views import (
    EmailSubscriptionListCreateView,
    EmailSubscriptionDetailView,
    verify_email_subscription,
    unsubscribe_email,
    subscription_stats
)

urlpatterns = [
    # Email subscription endpoints
    path('subscribe/', EmailSubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscribe/<int:pk>/', EmailSubscriptionDetailView.as_view(), name='subscription-detail'),
    path('subscribe/verify/<uuid:token>/', verify_email_subscription, name='verify-subscription'),
    path('subscribe/unsubscribe/', unsubscribe_email, name='unsubscribe'),
    path('subscribe/stats/', subscription_stats, name='subscription-stats'),
]
