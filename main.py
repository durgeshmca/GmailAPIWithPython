
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.gmail_service import GmailService
from services.llm_service import LLM

app = FastAPI()

class ReplyRequest(BaseModel):
    content: str
    from_: str = None

def get_labels():
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    try:
        gmail = GmailService(SCOPES)
        labels = gmail.get_labels()
        return labels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_labels")
async def get_labels_route():
    labels = get_labels()
    if isinstance(labels, dict) and "error" in labels:
        raise HTTPException(status_code=500, detail=labels["error"])
    return {"labels": labels}

@app.get("/get_latest_email")
async def get_email_route():
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    try:
        gmail = GmailService(SCOPES)
        emails = gmail.get_latest_emails()
        return {"emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_reply")
async def get_reply(data: ReplyRequest):
    if not data.content:
        raise HTTPException(status_code=400, detail="Missing 'content' key in JSON body")
    try:
        llm = LLM()
        reply = llm.get_reply(data.content, data.from_)
        return {"content": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create_draft")
async def create_reply_draft():
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/calendar'
    ]
    try:
        gmail = GmailService(SCOPES)
        response = gmail.create_draft_email()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")


