import secrets
import string
from django.contrib.auth.models import User
from django.db import IntegrityError, models, transaction

ALPHABET = string.ascii_letters + string.digits

class Link(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="links")
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        if self.short_code:
            return super().save(*args, **kwargs)
        for _ in range(8):
            self.short_code = "".join(secrets.choice(ALPHABET) for _ in range(7))
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                self.short_code = ""
        raise RuntimeError("Unable to allocate a unique short code")

class Click(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name="clicks")
    clicked_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user_agent = models.CharField(max_length=255, blank=True)
