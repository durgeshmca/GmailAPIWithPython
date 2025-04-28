
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os

class GoogleService():
    def __init__(self,scopes,service_name="gmail"):
        self._service_name = service_name
        self.service = self._get_service(scopes,service_name)
        
    def _get_service(self,scopes,service_name):
        creds = None
        if os.path.exists("creds/token.json"):
            creds = Credentials.from_authorized_user_file("creds/token.json", scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", scopes
                )
                creds = flow.run_local_server(bind_addr="0.0.0.0",open_browser=False,port=8002)
                            
            with open("/app/creds/token.json", "w") as token:
                token.write(creds.to_json())

        try:
            if service_name == 'calendar':
                service = build('calendar', 'v3', credentials=creds)
            else :
                service = build("gmail", "v1", credentials=creds)
            return service
        
        except HttpError as error:
            raise(f"error{error}")
