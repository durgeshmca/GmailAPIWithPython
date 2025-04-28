from flask import Flask, jsonify
from flask import request

from services.gmail_service import GmailService
from services.llm_service import LLM
# If modifying these scopes, delete the file token.json.
app = Flask(__name__)

def get_labels():
  SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
  try:
    gmail = GmailService(SCOPES)
    labels = gmail.get_labels()
    return labels
  except Exception as e:
    return {"error": str(e)}
  


@app.route("/get_labels")
def get_labels_route():
  labels = get_labels()
  if isinstance(labels, dict) and "error" in labels:
    return jsonify(labels), 500
  return jsonify({"labels": labels})


@app.route("/get_latest_email")
def get_email_route():
  SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
  try:
    gmail = GmailService(SCOPES)
    emails = gmail.get_latest_emails()
    return jsonify({"emails": emails})
  except Exception as e:
    return jsonify({"error": str(e)}), 500

@app.route("/get_reply", methods=["POST"])
def get_reply():
  
  data = None
  if not (data := request.get_json()):
    return jsonify({"error": "Missing JSON body"}), 400
  content = data.get("content")
  if content is None:
    return jsonify({"error": "Missing 'content' key in JSON body"}), 400
  try:
    llm = LLM()
    reply = llm.get_reply(content,data.get("from"))
    return jsonify({"content": reply})
  except Exception as e:
    return jsonify({"error": str(e)}), 500

@app.route("/create_draft", methods=["POST"])
def create_reply_draft():
  
  SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/calendar'
    ]
  try:
    gmail = GmailService(SCOPES)
    response = gmail.create_draft_email()
    return jsonify(response)
  except Exception as e:
    return jsonify({"error": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
  response = {
    "error": str(e)
  }
  return jsonify(response), 500

if __name__ == "__main__":
  app.run(debug=True,host="0.0.0.0",port=8001)

