
from django.shortcuts import redirect
from django.http import JsonResponse
import msal
import os
from azure_auth_demo import settings
import msal
import urllib.parse
import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse




def azure_login(request):
    params = {
        "client_id": settings.AZURE_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.AZURE_REDIRECT_URI,
        "scope": "openid profile email",
    }
    login_url = f"{settings.AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(login_url)


def azure_callback(request):
    code = request.GET.get("code")
    
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    token_data = {
        "client_id": settings.AZURE_CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "client_secret":settings.AZURE_CLIENT_SECRET,
        "redirect_uri": settings.AZURE_REDIRECT_URI,
    }

    response = requests.post(settings.TOKEN_URL, data=token_data)
    token_json = response.json()

    return JsonResponse(token_json)


def build_msal_app(cache=None):
    if cache is None:
        cache = msal.TokenCache()  

    return msal.ConfidentialClientApplication(
        settings.AZURE_CLIENT_ID,
        authority=settings.AZURE_AUTHORITY,
        client_credential=settings.AZURE_CLIENT_SECRET,
        token_cache=cache
    )


def login(request):
    msal_app = build_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=os.getenv("AZURE_SCOPE").split(","),
        redirect_uri=os.getenv("AZURE_REDIRECT_URI")
    )
    return redirect(auth_url)


def callback(request):
    code = request.GET.get("code", None)
    if not code:
        return JsonResponse({"error": "No code in request"}, status=400)
    
    try:
        
        msal_app = build_msal_a
        
        msal_app = build_msal_app()
        result = msal_app.acquire_token_by_authorization_code(code,
            scopes=settings.AZURE_SCOPE,
            redirect_uri=settings.AZURE_REDIRECT_URI
        )
        print("result:::::::::::::::", result)

        if "access_token" in result:
            request.session["access_token"] = result["access_token"]
            return JsonResponse({"token": result["access_token"]})
        else:
            return JsonResponse({"error": "Failed to acquire token", "details": result.get("error_description")}, status=401)

    except Exception as e:
        return JsonResponse({"error": "Unexpected error", "details": str(e)}, status=500)


    # msal_app = build_msal_app()
    # result = msal_app.acquire_token_by_authorization_code(
    #     code,
    #     scopes=os.getenv("AZURE_SCOPE").split(","),
    #     redirect_uri=os.getenv("AZURE_REDIRECT_URI")
    # )
    # print("result:::::::::::::::",result)
    # if "access_token" in result:
    #     return JsonResponse({"token": result["access_token"]})
    # else:
    #     return JsonResponse({"error": "Failed to acquire token", "details": result.get("error_description")})


class SecureAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return JsonResponse({"message": "You are authenticated via Azure AD!"})

