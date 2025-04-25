
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage
from llm_service import LLM
import os
import base64
class GmailService():
    def __init__(self,scopes):
        self.service = self._get_service(scopes)
        
    def _get_service(self,scopes):
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
                # print(creds.to_json())
            
            with open("/app/creds/token.json", "w") as token:
                token.write(creds.to_json())

        try:
            service = build("gmail", "v1", credentials=creds)
            return service
        except HttpError as error:
            return {"error": str(error)}
    
    def get_labels(self):
        try:
            results = self.service.users().labels().list(userId="me").execute()
            # print(results)
            labels = results.get("labels", [])
            # print(results)
            if not labels:
                return []
            return [label["name"] for label in labels]
        except Exception as error:
            return {"error": str(error)}
        
    def get_latest_emails(self, limit:int = 1):
        # print("\n=============== Find Emails: start ===============")
        results = (
            self.service.users()
            .messages()
            # .list(userId="me",labelIds=['UNREAD','INBOX'],q=f'label:inbox AND label:unread' , maxResults=limit)
            .list(userId="me",q=f'label:inbox AND label:unread' , maxResults=limit)
            .execute()
        )
        print(results)
        latest_unread = results.get("messages", [])
        if latest_unread :
            latest_id = latest_unread[0]['id']
            response = self.service.users().messages().get(userId="me", id=latest_id).execute()
            print(response)
            final_message = ""
            parts = response["payload"].get("parts",[])
            if len(parts) == 0 :
                parts.append({'body':response["payload"]['body']}) 
            for message in parts:
                content = message["body"]["data"]
                content = content.replace("-", "+").replace("_", "/")
                decoded = base64.b64decode(content).decode("utf-8")
                final_message += decoded
                break
            # headers = ['From','Subject']
            # print(response)
            print(final_message)
            headers = {header['name']:header['value'] for header in response["payload"]["headers"]}
            meta = {

                "from" : headers.get('Return-Path',''),
                "reply_message_id": headers.get('Message-ID',''),
                "to": headers.get('To',''),
                "subject" : headers.get('Subject',''),
                "thread_id" : response.get("threadId",''),
                "message_id" : response.get("id",''),
            }

        return {"message":final_message,"meta":meta}
    
    def get_message_reply(self,email):
        llm = LLM()
        reply = llm.get_reply(email['message'],email['meta']['from'])
        return reply
    
    def create_draft_email(self):
        # get latest message
        latest_email = self.get_latest_emails()
        # generate reply
        reply = self.get_message_reply(latest_email)
        if reply['reply']=='NA':
         
         return {
            "notice":"Latest message is not relevant to create draft.",
            "message": latest_email['message']
            }
        
        message = EmailMessage()
        message.set_content(reply['reply'])

        message["To"] = latest_email['meta']['from']
        message["From"] = latest_email['meta']['to']
        message["Subject"] = 'Re: '+latest_email['meta']['subject']
        message['In-Reply-To'] = latest_email['meta']['reply_message_id']
        message['References'] = latest_email['meta']['reply_message_id']
        # print(message)  

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message,"threadId":latest_email['meta']['thread_id']}}
        # pylint: disable=E1101
        draft = (
            self.service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )
        # print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

        return {
            'message_id' :latest_email['meta']['message_id'],
            'message': latest_email['message'],
            'draft_id': draft["id"],
            'draft_message': draft["message"]
            }

