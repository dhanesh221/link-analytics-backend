import json
import jwt
import requests
from jwt.algorithms import ECAlgorithm

SUPABASE_JWKS_URL = 'https://bnsoyijkurhqrpgrakzs.supabase.co/auth/v1/.well-known/jwks.json'

_key_cache = {}

def _get_public_key(kid):
    if kid not in _key_cache:
        resp = requests.get(SUPABASE_JWKS_URL, timeout=10)
        resp.raise_for_status()
        for key_data in resp.json().get('keys', []):
            _key_cache[key_data['kid']] = ECAlgorithm.from_jwk(json.dumps(key_data))
    return _key_cache.get(kid)

def verify_supabase_token(token):
    header = jwt.get_unverified_header(token)
    public_key = _get_public_key(header.get('kid'))
    if not public_key:
        raise ValueError('No matching public key found in Supabase JWKS')
    return jwt.decode(
        token,
        public_key,
        algorithms=['ES256'],
        options={'verify_aud': False},
    )
