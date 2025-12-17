from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import EmailSubscription, EmailCampaign


class EmailSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmailSubscription
        fields = [
            "id",
            "email",
            "subscription_type",
            "status",
            "frequency",
            "subscribed_at",
            "is_verified",
            "source",
        ]
        read_only_fields = ["id", "status", "subscribed_at", "is_verified"]

    def validate_email(self, value):
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value.lower()


class EmailSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new subscriptions"""

    agree_to_terms = serializers.BooleanField(write_only=True)

    class Meta:
        model = EmailSubscription
        fields = ["email", "subscription_type", "frequency", "source", "agree_to_terms"]

    def validate_agree_to_terms(self, value):
        if not value:
            raise serializers.ValidationError(
                "You must agree to receive email notifications."
            )
        return value

    def validate_email(self, value):
        email = value.lower()
        if EmailSubscription.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already subscribed.")
        return email

    def create(self, validated_data):
        validated_data.pop("agree_to_terms")  # Remove from data before creating
        validated_data["email"] = validated_data["email"].lower()
        return super().create(validated_data)


class EmailCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailCampaign
        fields = "__all__"
        read_only_fields = [
            "total_recipients",
            "delivered_count",
            "opened_count",
            "clicked_count",
        ]
