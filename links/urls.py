from django.urls import path
from .views import LinkListCreateView, LinkDetailView, RedirectLinkView, health, readiness
urlpatterns = [
    path("healthz/", health, name="health"),
    path("readyz/", readiness, name="readiness"),
    path("api/v1/links/", LinkListCreateView.as_view(), name="link-list-create"),
    path("api/v1/links/<int:pk>/", LinkDetailView.as_view(), name="link-detail"),
    path("r/<str:short_code>/", RedirectLinkView.as_view(), name="redirect-link"),
]
