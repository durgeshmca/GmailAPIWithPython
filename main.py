from flask import Flask, jsonify
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

app = Flask(__name__)

def get_labels():
  """Gets the user's Gmail labels and returns them as a list."""
  creds = None
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(bind_addr="0.0.0.0",open_browser=False,port=8002)
      print(creds.to_json())
    with open("/app/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])
    if not labels:
      return []
    return [label["name"] for label in labels]
  except HttpError as error:
    return {"error": str(error)}

@app.route("/get_labels")
def get_labels_route():
  labels = get_labels()
  if isinstance(labels, dict) and "error" in labels:
    return jsonify(labels), 500
  return jsonify({"labels": labels})

if __name__ == "__main__":
  app.run(debug=False,host="0.0.0.0",port=8001)
