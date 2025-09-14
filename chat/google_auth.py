import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login

def get_google_oauth_url():
    """Generate Google OAuth URL"""
    return (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.GOOGLE_OAUTH2_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_OAUTH2_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline&"
        f"prompt=select_account"
    )

def exchange_code_for_token(code):
    """Exchange authorization code for access token"""
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return None
    
    return response.json()

def get_user_info(access_token):
    """Get user info from Google API"""
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(user_info_url, headers=headers)
    
    if response.status_code != 200:
        return None
    
    return response.json()

def authenticate_user(user_info):
    """Authenticate or create user based on Google info"""
    try:
        user = User.objects.get(email=user_info['email'])
    except User.DoesNotExist:
        # Create a new user
        username = user_info['email'].split('@')[0]
        # Ensure username is unique
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
            
        user = User.objects.create_user(
            username=username,
            email=user_info['email'],
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', '')
        )
    
    return user