from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import uuid
from .models import EmailSubscription
from .serializers import EmailSubscriptionSerializer, EmailSubscriptionCreateSerializer



class EmailSubscriptionListCreateView(generics.ListCreateAPIView):
    """
    GET: List all email subscriptions (admin only)
    POST: Create new email subscription (public)
    """
    queryset = EmailSubscription.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'subscription_type', 'frequency', 'is_verified']
    search_fields = ['email', 'subscription_type', 'source']
    ordering_fields = ['subscribed_at', 'updated_at']
    ordering = ['-subscribed_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmailSubscriptionCreateSerializer
        return EmailSubscriptionSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # Get client IP and user agent
        ip_address = self.get_client_ip()
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        serializer.save(
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class EmailSubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve specific subscription
    PUT/PATCH: Update subscription
    DELETE: Delete subscription
    """
    queryset = EmailSubscription.objects.all()
    serializer_class = EmailSubscriptionSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_subscription(request, token):
    """Verify email subscription using token"""
    try:
        subscription = EmailSubscription.objects.get(verification_token=token)
        if subscription.is_verified:
            return Response({
                'message': 'Email is already verified.'
            }, status=status.HTTP_200_OK)
        
        subscription.verify_email()
        return Response({
            'message': 'Email verified successfully! You are now subscribed to receive notifications.'
        }, status=status.HTTP_200_OK)
        
    except EmailSubscription.DoesNotExist:
        return Response({
            'error': 'Invalid verification token.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe_email(request):
    """Unsubscribe email using email address or token"""
    email = request.data.get('email')
    token = request.data.get('token')
    
    if not email and not token:
        return Response({
            'error': 'Email address or token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if token:
            subscription = EmailSubscription.objects.get(verification_token=token)
        else:
            subscription = EmailSubscription.objects.get(email=email.lower())
        
        if subscription.status == 'unsubscribed':
            return Response({
                'message': 'Email is already unsubscribed.'
            }, status=status.HTTP_200_OK)
        
        subscription.unsubscribe()
        return Response({
            'message': 'Successfully unsubscribed from email notifications.'
        }, status=status.HTTP_200_OK)
        
    except EmailSubscription.DoesNotExist:
        return Response({
            'error': 'Subscription not found.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def subscription_stats(request):
    """Get subscription statistics"""
    total_subscriptions = EmailSubscription.objects.count()
    active_subscriptions = EmailSubscription.objects.filter(status='active').count()
    pending_subscriptions = EmailSubscription.objects.filter(status='pending').count()
    unsubscribed = EmailSubscription.objects.filter(status='unsubscribed').count()
    
    stats = {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'pending_subscriptions': pending_subscriptions,
        'unsubscribed': unsubscribed,
        'subscription_types': {}
    }
    
    # Get stats by subscription type
    for choice in EmailSubscription.SUBSCRIPTION_TYPES:
        type_key = choice[0]
        count = EmailSubscription.objects.filter(
            subscription_type=type_key, 
            status='active'
        ).count()
        stats['subscription_types'][type_key] = count
    
    return Response(stats)
