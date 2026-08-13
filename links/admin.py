from django.contrib import admin
from .models import Link, Click

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['short_code', 'owner', 'original_url', 'created_at']
    list_filter = ['owner']
    search_fields = ['short_code', 'original_url']

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ['link', 'clicked_at', 'ip_address', 'user_agent']
    list_filter = ['link']
