from rest_framework.serializers import ModelSerializer
from .models import MyLink, ClickAnalytics
from rest_framework import serializers


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyLink
        fields = '__all__'
        read_only_fields = ['hash', 'user']

    def validate(self, attrs):
        # Get request from context
        request = self.context.get('request')
        
        # Check if user is trying to set expiration date without authentication
        if attrs.get('expiration_date') and not (request and request.user.is_authenticated):
            raise serializers.ValidationError(
                {"expiration_date": "Authentication required to set expiration date"}
            )
        return attrs

class ClickAnalyticsSerializer(ModelSerializer):
    class Meta:
        model = ClickAnalytics
        fields = '__all__'        