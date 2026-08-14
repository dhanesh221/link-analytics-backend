from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Link, Click
from .serializers import LinkSerializer, RegisterSerializer
from .supabase_auth import verify_supabase_token

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class SupabaseAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = verify_supabase_token(token)
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        supabase_id = payload.get('sub')
        email = payload.get('email', '')

        if not supabase_id:
            return Response({'error': 'Invalid token payload'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            username=supabase_id,
            defaults={'email': email},
        )
        if not created and user.email != email:
            user.email = email
            user.save(update_fields=['email'])

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

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
