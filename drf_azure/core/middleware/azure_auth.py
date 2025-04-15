from jose import jwt
import requests
from django.contrib.auth.models import User, Group
from django.utils.deprecation import MiddlewareMixin
import os

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")

class AzureADAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header or not auth_header.startswith("Bearer "):
            return

        token = auth_header.split(" ")[1]
        user_info = self._verify_token(token)
        if user_info:
            user, _ = User.objects.get_or_create(username=user_info["preferred_username"])
            user.email = user_info.get("email", "")
            user.save()

            for role in user_info.get("roles", []):
                group, _ = Group.objects.get_or_create(name=role)
                user.groups.add(group)

            request.user = user

    def _verify_token(self, token):
        try:
            jwks_uri = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"
            jwks = requests.get(jwks_uri).json()
            unverified_header = jwt.get_unverified_header(token)
            key = next(
                (k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None
            )
            if key is None:
                return None

            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=CLIENT_ID,
                issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            )
            return claims
        except Exception as e:
            return None
