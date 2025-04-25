from groq import Groq
import os
class LLM():
    def __init__(self,model=os.environ.get('MODEL_NAME')):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = model

    def get_reply(self,email_content:str,from_:str):


        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful email assistant of a Software engineer Expert who have great experience in creating websites , ecomerce plateforms and chatbot. \n First check if this email is related to the software development then create a reply message.Make sure you only create reply message no extra words, If email is not related to the software development just reply with \"NA\"\n"
                },
                {
                    "role": "user",
                    "content": f"\nFrom:{from_}\nEmail content:{email_content}"
                }
            ],
            temperature=0,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        return {'reply':completion.choices[0].message.content}
