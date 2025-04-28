from langchain.tools import tool
import datetime
from typing import Annotated
from services.calendar_service import CalendarService
@tool
def calendar_event_create_tool(
    summary:Annotated[str, "summary of event"],
    description:Annotated[str, "description of event"],
    start_date_time_iso_format:Annotated[str, "start date and time of event in iso format"],
    end_date_time_iso_format:Annotated[str, "end date and time of event in iso format"],
    attendees_emails:Annotated[str, "comma separated event attendees emails"],
    timezone:Annotated[str, "timezone for  event default should be `Asia/Kolkata`"]='Asia/Kolkatta',
    
    )->dict[str:any]:
        '''Call this tool to create an calaender event.'''
    # Create an event
        # obj = [ summary,description, start_date_time_iso_format,end_date_time_iso_format,attendees_emails]
        # print(obj)
        attendees_emails =[ {'email': email.strip()} for email in attendees_emails.split(',')]
        format_string = '%Y-%m-%dT%H:%M:%S%z'
        event_object = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': datetime.datetime.strptime(start_date_time_iso_format,format_string).isoformat(), 
                'timeZone': timezone,
            },
            'end': {
                'dateTime': datetime.datetime.strptime(end_date_time_iso_format,format_string).isoformat(),
                'timeZone': timezone,

            },
            "attendees":attendees_emails
        }
        # print(event_object)
        SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/calendar'
        ]
        service = CalendarService(SCOPES)
        return service.create_event(event_object)

