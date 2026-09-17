import json
import os
import threading
import time

import jwt
import requests
from django.contrib.auth import get_user_model
from jwt.algorithms import ECAlgorithm, RSAAlgorithm
from rest_framework import authentication, exceptions

_cache = {"keys": {}, "expires_at": 0.0}
_lock = threading.Lock()


def _settings():
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    issuer = os.environ.get("SUPABASE_JWT_ISSUER", f"{url}/auth/v1" if url else "")
    audience = os.environ.get("SUPABASE_JWT_AUDIENCE", "authenticated")
    if not url or not issuer or not audience:
        raise exceptions.AuthenticationFailed("Supabase authentication is not configured")
    return url, issuer, audience


def _load_keys(force=False):
    url, _, _ = _settings()
    now = time.monotonic()
    with _lock:
        if not force and _cache["keys"] and now < _cache["expires_at"]:
            return _cache["keys"]
        try:
            response = requests.get(f"{url}/auth/v1/.well-known/jwks.json", timeout=5)
            response.raise_for_status()
            keys = {}
            for jwk in response.json().get("keys", []):
                kid = jwk.get("kid")
                if not kid:
                    continue
                loader = ECAlgorithm if jwk.get("kty") == "EC" else RSAAlgorithm
                keys[kid] = loader.from_jwk(json.dumps(jwk))
        except (requests.RequestException, ValueError, KeyError) as exc:
            raise exceptions.AuthenticationFailed("Unable to verify access token") from exc
        if not keys:
            raise exceptions.AuthenticationFailed("No signing keys are available")
        _cache.update(keys=keys, expires_at=now + 3600)
        return keys


def verify_supabase_token(token):
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise exceptions.AuthenticationFailed("Invalid access token") from exc
    algorithm = header.get("alg")
    if algorithm not in {"ES256", "RS256"}:
        raise exceptions.AuthenticationFailed("Unsupported token algorithm")
    kid = header.get("kid")
    key = _load_keys().get(kid)
    if key is None:
        key = _load_keys(force=True).get(kid)
    if key is None:
        raise exceptions.AuthenticationFailed("Unknown signing key")
    _, issuer, audience = _settings()
    try:
        return jwt.decode(token, key, algorithms=[algorithm], issuer=issuer, audience=audience)
    except jwt.PyJWTError as exc:
        raise exceptions.AuthenticationFailed("Invalid or expired access token") from exc


class SupabaseAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        value = authentication.get_authorization_header(request).decode("utf-8")
        if not value:
            return None
        parts = value.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed("Invalid authorization header")
        payload = verify_supabase_token(parts[1])
        subject = payload.get("sub")
        if not subject:
            raise exceptions.AuthenticationFailed("Token subject is missing")
        email = payload.get("email", "")
        user, created = get_user_model().objects.get_or_create(username=subject, defaults={"email": email})
        if not created and email and user.email != email:
            user.email = email
            user.save(update_fields=["email"])
        return user, payload
