from rest_framework import serializers
from .models import Link

class LinkSerializer(serializers.ModelSerializer):
    click_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Link
        fields = ["id", "original_url", "short_code", "is_active", "created_at", "click_count"]
        read_only_fields = ["short_code", "created_at", "click_count"]

    def validate_original_url(self, value):
        if value.lower().startswith(("http://", "https://")):
            return value
        raise serializers.ValidationError("Only HTTP and HTTPS destinations are allowed.")
