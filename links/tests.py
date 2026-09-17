from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Click, Link

@override_settings(SECURE_SSL_REDIRECT=False)
class LinkApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user-1")
        self.other = User.objects.create_user("user-2")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    def test_list_is_owner_scoped(self):
        Link.objects.create(owner=self.user, original_url="https://example.com/a")
        Link.objects.create(owner=self.other, original_url="https://example.com/b")
        response = self.client.get("/api/v1/links/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
    def test_create_rejects_non_http_url(self):
        response = self.client.post("/api/v1/links/", {"original_url": "ftp://example.com"})
        self.assertEqual(response.status_code, 400)
    def test_detail_cannot_cross_owner_boundary(self):
        link = Link.objects.create(owner=self.other, original_url="https://example.com")
        self.assertEqual(self.client.get(f"/api/v1/links/{link.id}/").status_code, 404)
    def test_redirect_records_click(self):
        link = Link.objects.create(owner=self.user, original_url="https://example.com")
        self.client.force_authenticate(None)
        response = self.client.get(f"/r/{link.short_code}/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Click.objects.filter(link=link).count(), 1)
    @patch("links.models.Click.objects.create", side_effect=RuntimeError("database unavailable"))
    def test_tracking_failure_does_not_break_redirect(self, _):
        link = Link.objects.create(owner=self.user, original_url="https://example.com")
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(f"/r/{link.short_code}/").status_code, 302)
