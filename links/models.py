from django.db import models
from django.contrib.auth.models import User
import string, random

class Link(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='links')
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self._generate_code()
        super().save(*args, **kwargs)

    def _generate_code(self):
        chars = string.ascii_letters + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            if not Link.objects.filter(short_code=code).exists():
                return code

class Click(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='clicks')
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
