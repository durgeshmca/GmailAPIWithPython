from email.message import EmailMessage
# from llm_service import LLM
from .google_service import GoogleService
from googleapiclient.errors import HttpError
# import datetime
# import base64
class CalendarService(GoogleService):
    def __init__(self,scopes):
        super().__init__(scopes,'calendar')
    
    def create_event(self,event_object):
        try:
            created_event = self.service.events().insert(calendarId='primary', body=event_object,sendUpdates='all').execute()
            # print(f'Event created: {created_event.get("htmlLink")}')
            return {"message":created_event.get("htmlLink")}
           

        except HttpError as error:
            raise(f'An error occurred: {error}')
