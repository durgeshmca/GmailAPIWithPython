from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent,AgentExecutor
from tools.calendar_tool import calendar_event_create_tool

import os
class LLM():
    def __init__(self,model=os.environ.get('MODEL_NAME')):
        self.client = ChatGroq(
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0,
            max_completion_tokens=1024,
            top_p=1,
            model = model
            )
        self.model = model

    def get_reply(self,email_content:str,from_:str):
        messages=[
               ("system","You are a helpful email assistant of a Software engineer Expert who have great experience in creating websites , ecomerce plateforms and chatbot. \n First check if this email is related to the software development then create a reply message.Make sure you only create reply message no extra words. If possible use tool `calendar_event_create_tool` when required to schedule an online meeting. If email is not related to the software development just reply with \"NA\"\n")
                ,
                ("user",f"\nFrom:{from_}\nEmail content:{email_content}"),
                ("placeholder", "{agent_scratchpad}"),
                
            ]
        prompt = ChatPromptTemplate.from_messages(messages)
        tools = [calendar_event_create_tool]
        #  create agent
        agent = create_tool_calling_agent(self.client,tools,prompt)
        # create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
        )
        output = agent_executor.invoke({"from_":from_,"email_content":email_content})

        return {'reply':output}
