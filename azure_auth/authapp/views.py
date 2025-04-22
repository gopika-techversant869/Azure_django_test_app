
from django.shortcuts import redirect
from django.http import JsonResponse
import msal
import os

def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        os.getenv("AZURE_CLIENT_ID"),
        authority=os.getenv("AZURE_AUTHORITY"),
        client_credential=os.getenv("AZURE_CLIENT_SECRET"),
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

    msal_app = build_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=os.getenv("AZURE_SCOPE").split(","),
        redirect_uri=os.getenv("AZURE_REDIRECT_URI")
    )

    if "access_token" in result:
        return JsonResponse({"token": result["access_token"]})
    else:
        return JsonResponse({"error": "Failed to acquire token", "details": result.get("error_description")})
