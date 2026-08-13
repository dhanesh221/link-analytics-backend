from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, LinkListCreateView, LinkDetailView, RedirectLinkView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/links/', LinkListCreateView.as_view(), name='link-list-create'),
    path('api/links/<int:pk>/', LinkDetailView.as_view(), name='link-detail'),
    path('r/<str:short_code>/', RedirectLinkView.as_view(), name='redirect-link'),
]
