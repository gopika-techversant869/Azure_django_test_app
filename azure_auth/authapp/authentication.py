import jwt
import requests
from azure_auth_demo import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class AzureADAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")

        if not token:
            return None

        try:
            token = token.split(" ")[1]  
            jwks_url = f"https://login.microsoftonline.com/{settings.AZURE_AUTHORITY}/discovery/keys"
            keys = requests.get(jwks_url).json()

            decoded_token = jwt.decode(token, keys, algorithms=["RS256"], audience=settings.AZURE_CLIENT_ID)

            return (decoded_token, None)
        
        except Exception:
            raise AuthenticationFailed("Invalid token")
