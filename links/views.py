import logging
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import Click, Link
from .serializers import LinkSerializer
from .throttles import LinkCreateThrottle

logger = logging.getLogger(__name__)

class LinkListCreateView(generics.ListCreateAPIView):
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Link.objects.filter(owner=self.request.user).annotate(click_count=Count("clicks")).order_by("-created_at")
    def get_throttles(self):
        return [LinkCreateThrottle()] if self.request.method == "POST" else super().get_throttles()
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LinkDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Link.objects.filter(owner=self.request.user).annotate(click_count=Count("clicks"))

class RedirectLinkView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = []
    def get(self, request, short_code):
        link = get_object_or_404(Link, short_code=short_code, is_active=True)
        try:
            Click.objects.create(link=link, user_agent=request.META.get("HTTP_USER_AGENT", "")[:255])
        except Exception:
            logger.exception("click_record_failed", extra={"link_id": link.id})
        return HttpResponseRedirect(link.original_url)

def health(request):
    return JsonResponse({"status": "ok"})

def readiness(request):
    from django.db import connection
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ready"})
