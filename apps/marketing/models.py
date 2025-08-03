from django.db import models
from django.utils import timezone
import uuid


class EmailSubscription(models.Model):
    """Model for email newsletter subscriptions"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('unsubscribed', 'Unsubscribed'),
        ('pending', 'Pending Verification'),
        ('bounced', 'Bounced'),
    ]
    
    SUBSCRIPTION_TYPES = [
        ('newsletter', 'Newsletter'),
        ('updates', 'Product Updates'),
        ('promotions', 'Promotions'),
        ('all', 'All Notifications'),
    ]
    
    email = models.EmailField(unique=True, db_index=True)
    subscription_type = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_TYPES, 
        default='newsletter'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unsubscribed_at = models.DateTimeField(blank=True, null=True)
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_verified = models.BooleanField(default=False)
    source = models.CharField(max_length=100, blank=True, null=True)  # Where they subscribed from
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

     # Preferences
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['status', 'subscription_type']),
        ]
        
    def __str__(self):
        return f"{self.email} ({self.status})"
    
    def unsubscribe(self):
        """Mark subscription as unsubscribed"""
        self.status = 'unsubscribed'
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def verify_email(self):
        """Mark email as verified"""
        self.is_verified = True
        self.status = 'active'
        self.save()


class EmailCampaign(models.Model):
    """Model for email campaigns"""
    CAMPAIGN_TYPES = [
        ('newsletter', 'Newsletter'),
        ('promotional', 'Promotional'),
        ('announcement', 'Announcement'),
        ('welcome', 'Welcome Series'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Targeting
    target_subscription_types = models.JSONField(default=list)  # Which subscription types to send to
    
    # Scheduling
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # Metrics
    total_recipients = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    opened_count = models.PositiveIntegerField(default=0)
    clicked_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

