from email.message import EmailMessage
from services.llm_service import LLM
from services.google_service import GoogleService
import base64
class GmailService(GoogleService):
    def __init__(self,scopes):
        super().__init__(scopes,'gmail')
    
    def get_labels(self):
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
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
        latest_unread = results.get("messages", [])
        if latest_unread :
            latest_id = latest_unread[0]['id']
            response = self.service.users().messages().get(userId="me", id=latest_id).execute()
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
        # print(reply)
        if reply['reply']['output']=='NA':
         
         return {
            "notice":"Latest message is not relevant to create draft.",
            "message": latest_email['message']
            }
        
        message = EmailMessage()
        message.set_content(reply['reply']['output'])

        message["To"] = latest_email['meta']['from']
        message["From"] = latest_email['meta']['to']
        message["Subject"] = 'Re: '+latest_email['meta']['subject']
        message['In-Reply-To'] = latest_email['meta']['reply_message_id']
        message['References'] = latest_email['meta']['reply_message_id']
        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"message": {"raw": encoded_message,"threadId":latest_email['meta']['thread_id']}}
        draft = (
            self.service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )
    
        return {
            'message_id' :latest_email['meta']['message_id'],
            'message': latest_email['message'],
            'draft_id': draft["id"],
            'draft_message': draft["message"]
            }

