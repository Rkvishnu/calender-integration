 # views.py
import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View

GOOGLE_OAUTH2_AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_OAUTH2_TOKEN_ENDPOINT = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_CALENDAR_API_ENDPOINT = 'https://www.googleapis.com/calendar/v3'

class GoogleCalendarInitView(View):
    def get(self, request):
        # Step 1: Redirect the user to the Google OAuth2 authorization page
        redirect_uri = request.build_absolute_uri(reverse('google-calendar-redirect'))
        auth_url = f"{GOOGLE_OAUTH2_AUTH_ENDPOINT}?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&scope=https://www.googleapis.com/auth/calendar.readonly&response_type=code"
        return HttpResponseRedirect(auth_url)

class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Step 2: Exchange the authorization code for an access token
        code = request.GET.get('code')
        redirect_uri = request.build_absolute_uri(reverse('google-calendar-redirect'))
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = requests.post(GOOGLE_OAUTH2_TOKEN_ENDPOINT, data=data)
        token_data = json.loads(response.text)
        
        # Step 3: Use the access token to fetch the list of events from the user's calendar
        access_token = token_data.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        events_url = f"{GOOGLE_CALENDAR_API_ENDPOINT}/events"
        events_response = requests.get(events_url, headers=headers)
        events_data = json.loads(events_response.text)
        
        return JsonResponse(events_data, safe=False)
