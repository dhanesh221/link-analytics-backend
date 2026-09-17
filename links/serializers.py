from rest_framework import serializers
from .models import Link

class LinkSerializer(serializers.ModelSerializer):
    click_count = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ["id", "original_url", "short_code", "is_active", "created_at", "click_count"]
        read_only_fields = ["short_code", "created_at", "click_count"]

    def get_click_count(self, link):
        annotated_count = getattr(link, "click_count", None)
        return annotated_count if annotated_count is not None else link.clicks.count()

    def validate_original_url(self, value):
        if value.lower().startswith(("http://", "https://")):
            return value
        raise serializers.ValidationError("Only HTTP and HTTPS destinations are allowed.")
