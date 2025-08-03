# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
import csv
from .models import EmailSubscription, EmailCampaign


class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'subscription_type', 
        'status_badge', 
        'frequency', 
        'is_verified_badge',
        'subscribed_at',
        'source',
        'actions_column'
    ]
    
    list_filter = [
        'status', 
        'subscription_type', 
        'frequency', 
        'is_verified',
        'subscribed_at',
        'source'
    ]
    
    search_fields = [
        'email', 
        'first_name', 
        'last_name', 
        'source'
    ]
    
    readonly_fields = [
        'verification_token',
        'subscribed_at',
        'updated_at',
        'unsubscribed_at',
        'ip_address',
        'user_agent'
    ]
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email',)
        }),
        ('Subscription Settings', {
            'fields': ('subscription_type', 'status', 'frequency', 'source')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_token'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('subscribed_at', 'updated_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-subscribed_at']
    date_hierarchy = 'subscribed_at'
    list_per_page = 50
    
    
    def status_badge(self, obj):
        colors = {
            'active': 'success',
            'pending': 'warning',
            'unsubscribed': 'danger',
            'bounced': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span class="badge badge-success">✓ Verified</span>'
            )
        else:
            return format_html(
                '<span class="badge badge-warning">⚠ Unverified</span>'
            )
    is_verified_badge.short_description = 'Verification'
    is_verified_badge.admin_order_field = 'is_verified'
    
    def actions_column(self, obj):
        actions = []
        
        if obj.status == 'pending' and not obj.is_verified:
            verify_url = reverse('admin:verify_subscription', args=[obj.pk])
            actions.append(f'<a href="{verify_url}" class="btn btn-sm btn-success">Verify</a>')
        
        if obj.status != 'unsubscribed':
            unsubscribe_url = reverse('admin:unsubscribe_subscription', args=[obj.pk])
            actions.append(f'<a href="{unsubscribe_url}" class="btn btn-sm btn-warning">Unsubscribe</a>')
        
        if obj.status == 'unsubscribed':
            resubscribe_url = reverse('admin:resubscribe_subscription', args=[obj.pk])
            actions.append(f'<a href="{resubscribe_url}" class="btn btn-sm btn-primary">Resubscribe</a>')
        
        return format_html(' '.join(actions))
    actions_column.short_description = 'Actions'
    
    # Custom actions
    actions = [
        'export_to_csv',
        'mark_as_active',
        'mark_as_unsubscribed',
        'verify_selected',
        'send_verification_email'
    ]
    
    def export_to_csv(self, request, queryset):
        """Export selected subscriptions to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="email_subscriptions.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Email', 'Subscription Type',
            'Status', 'Frequency', 'Is Verified', 'Subscribed At', 'Source'
        ])
        
        for subscription in queryset:
            writer.writerow([
                subscription.email,
                subscription.get_subscription_type_display(),
                subscription.get_status_display(),
                subscription.get_frequency_display(),
                'Yes' if subscription.is_verified else 'No',
                subscription.subscribed_at.strftime('%Y-%m-%d %H:%M:%S'),
                subscription.source or ''
            ])
        
        self.message_user(request, f"Exported {queryset.count()} subscriptions to CSV.")
        return response
    export_to_csv.short_description = "Export selected to CSV"
    
    def mark_as_active(self, request, queryset):
        """Mark selected subscriptions as active"""
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} subscriptions marked as active.")
    mark_as_active.short_description = "Mark selected as active"
    
    def mark_as_unsubscribed(self, request, queryset):
        """Mark selected subscriptions as unsubscribed"""
        updated = queryset.update(
            status='unsubscribed',
            unsubscribed_at=timezone.now()
        )
        self.message_user(request, f"{updated} subscriptions marked as unsubscribed.")
    mark_as_unsubscribed.short_description = "Mark selected as unsubscribed"
    
    def verify_selected(self, request, queryset):
        """Verify selected subscriptions"""
        updated = queryset.filter(is_verified=False).update(
            is_verified=True,
            status='active'
        )
        self.message_user(request, f"{updated} subscriptions verified.")
    verify_selected.short_description = "Verify selected subscriptions"
    
    def send_verification_email(self, request, queryset):
        """Send verification email to selected unverified subscriptions"""
        unverified = queryset.filter(is_verified=False, status='pending')
        count = 0
        
        for subscription in unverified:
            # Here you would integrate with your email service
            # For now, we'll just simulate sending
            count += 1
        
        self.message_user(
            request, 
            f"Verification emails sent to {count} subscribers.",
            messages.SUCCESS
        )
    send_verification_email.short_description = "Send verification emails"
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:subscription_id>/verify/',
                self.admin_site.admin_view(self.verify_subscription),
                name='verify_subscription',
            ),
            path(
                '<int:subscription_id>/unsubscribe/',
                self.admin_site.admin_view(self.unsubscribe_subscription),
                name='unsubscribe_subscription',
            ),
            path(
                '<int:subscription_id>/resubscribe/',
                self.admin_site.admin_view(self.resubscribe_subscription),
                name='resubscribe_subscription',
            ),
        ]
        return custom_urls + urls
    
    def verify_subscription(self, request, subscription_id):
        """Custom view to verify a subscription"""
        subscription = EmailSubscription.objects.get(pk=subscription_id)
        subscription.verify_email()
        messages.success(request, f"Subscription for {subscription.email} has been verified.")
        return redirect('admin:myapp_emailsubscription_changelist')
    
    def unsubscribe_subscription(self, request, subscription_id):
        """Custom view to unsubscribe a subscription"""
        subscription = EmailSubscription.objects.get(pk=subscription_id)
        subscription.unsubscribe()
        messages.success(request, f"Subscription for {subscription.email} has been unsubscribed.")
        return redirect('admin:myapp_emailsubscription_changelist')
    
    def resubscribe_subscription(self, request, subscription_id):
        """Custom view to resubscribe a subscription"""
        subscription = EmailSubscription.objects.get(pk=subscription_id)
        subscription.status = 'active'
        subscription.unsubscribed_at = None
        subscription.save()
        messages.success(request, f"Subscription for {subscription.email} has been reactivated.")
        return redirect('admin:myapp_emailsubscription_changelist')
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to the changelist view"""
        extra_context = extra_context or {}
        
        # Get subscription statistics
        total_count = EmailSubscription.objects.count()
        active_count = EmailSubscription.objects.filter(status='active').count()
        pending_count = EmailSubscription.objects.filter(status='pending').count()
        unsubscribed_count = EmailSubscription.objects.filter(status='unsubscribed').count()
        verified_count = EmailSubscription.objects.filter(is_verified=True).count()
        
        extra_context['subscription_stats'] = {
            'total': total_count,
            'active': active_count,
            'pending': pending_count,
            'unsubscribed': unsubscribed_count,
            'verified': verified_count,
            'unverified': total_count - verified_count,
        }
        
        return super().changelist_view(request, extra_context=extra_context)


class EmailCampaignAdmin(admin.ModelAdmin):
    # class Media:
    #     css = {
    #         'all': ('admin/css/custom_admin.css',)
    #     }
    #     js = ('admin/js/custom_admin.js',)
    list_display = [
        'title',
        'campaign_type',
        'status_badge',
        'total_recipients',
        'delivered_count',
        'opened_count',
        'clicked_count',
        'open_rate',
        'click_rate',
        'created_at'
    ]
    
    list_filter = [
        'campaign_type',
        'status',
        'created_at',
        'scheduled_at'
    ]
    
    search_fields = ['title', 'subject']
    
    readonly_fields = [
        'total_recipients',
        'delivered_count',
        'opened_count',
        'clicked_count',
        'sent_at',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Campaign Information', {
            'fields': ('title', 'subject', 'content', 'campaign_type')
        }),
        ('Targeting', {
            'fields': ('target_subscription_types',)
        }),
        ('Scheduling', {
            'fields': ('status', 'scheduled_at', 'sent_at')
        }),
        ('Metrics', {
            'fields': (
                'total_recipients', 'delivered_count', 'opened_count', 
                'clicked_count'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'draft': 'secondary',
            'scheduled': 'info',
            'sent': 'success',
            'cancelled': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def open_rate(self, obj):
        if obj.delivered_count > 0:
            rate = (obj.opened_count / obj.delivered_count) * 100
            return f"{rate:.1f}%"
        return "0%"
    open_rate.short_description = 'Open Rate'
    
    def click_rate(self, obj):
        if obj.delivered_count > 0:
            rate = (obj.clicked_count / obj.delivered_count) * 100
            return f"{rate:.1f}%"
        return "0%"
    click_rate.short_description = 'Click Rate'


# Register the models
admin.site.register(EmailSubscription, EmailSubscriptionAdmin)
admin.site.register(EmailCampaign, EmailCampaignAdmin)

# Customize admin site headers
admin.site.site_header = "Email Subscription Management"
admin.site.site_title = "Email Admin"
admin.site.index_title = "Email Subscription Dashboard"


# Add custom CSS for better styling (optional)
class Media:
    css = {
        'all': ('admin/css/custom_admin.css',)
    }
    js = ('admin/js/custom_admin.js',)


# Custom admin CSS (create this file: static/admin/css/custom_admin.css)
"""
.badge {
    display: inline-block;
    padding: 0.25em 0.4em;
    font-size: 75%;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: 0.25rem;
}

.badge-success { background-color: #28a745; color: white; }
.badge-warning { background-color: #ffc107; color: black; }
.badge-danger { background-color: #dc3545; color: white; }
.badge-info { background-color: #17a2b8; color: white; }
.badge-secondary { background-color: #6c757d; color: white; }
.badge-primary { background-color: #007bff; color: white; }

.btn {
    display: inline-block;
    font-weight: 400;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    border: 1px solid transparent;
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
    line-height: 1.5;
    border-radius: 0.25rem;
    text-decoration: none;
    margin-right: 5px;
}

.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    line-height: 1.5;
    border-radius: 0.2rem;
}

.btn-success { background-color: #28a745; border-color: #28a745; color: white; }
.btn-warning { background-color: #ffc107; border-color: #ffc107; color: black; }
.btn-primary { background-color: #007bff; border-color: #007bff; color: white; }

.subscription-stats {
    background: #f8f9fa;
    padding: 15px;
    margin: 15px 0;
    border-radius: 5px;
    border: 1px solid #dee2e6;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
}

.stat-item {
    text-align: center;
    padding: 10px;
    background: white;
    border-radius: 3px;
    border: 1px solid #e9ecef;
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: #495057;
}

.stat-label {
    font-size: 12px;
    color: #6c757d;
    text-transform: uppercase;
}
"""