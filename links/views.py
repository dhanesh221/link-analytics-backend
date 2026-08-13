from rest_framework import generics, permissions
from rest_framework.views import APIView
from django.shortcuts import redirect, get_object_or_404
from .models import Link, Click
from .serializers import LinkSerializer, RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class LinkListCreateView(generics.ListCreateAPIView):
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Link.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LinkDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = LinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Link.objects.filter(owner=self.request.user)

class RedirectLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, short_code):
        link = get_object_or_404(Link, short_code=short_code)
        Click.objects.create(
            link=link,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return redirect(link.original_url)

