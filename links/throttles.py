from rest_framework.throttling import UserRateThrottle
class LinkCreateThrottle(UserRateThrottle):
    scope = "link_create"
