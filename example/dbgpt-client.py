import asyncio
from dbgpt.client import Client

DBGPT_API_KEY = "dbgpt"
LLM_MODEL = "/models/openbuddy"
SPACE_NAME = "edu_lib_v1"

async def chat_knowledge_lib():

    client = Client(api_key=DBGPT_API_KEY)
    async for data in client.chat_stream(model=LLM_MODEL,
                                         messages="hello",
                                         chat_model="chat_knowledge",
                                         chat_param=SPACE_NAME):
        print(data.choices[0].delta.content)

if __name__ == "__main__":

    asyncio.run(chat_knowledge_lib())
