from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Link

class LinkSerializer(serializers.ModelSerializer):
    click_count = serializers.SerializerMethodField()

    class Meta:
        model = Link
        fields = ['id', 'original_url', 'short_code', 'created_at', 'click_count']
        read_only_fields = ['short_code', 'created_at']

    def get_click_count(self, obj):
        return obj.clicks.count()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

