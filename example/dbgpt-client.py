import asyncio
from dbgpt.client import Client

DBGPT_API_BASE = "http://127.0.0.1:5670/api/v2"
DBGPT_API_KEY = "dbgpt"
LLM_MODEL = "/models/openbuddy"
CHAT_MODEL = "chat_knowledge"
SPACE_NAME = "edu_lib_v2-2"


class AsyncToSyncIterator:
    def __init__(self, async_gen):
        self.async_gen = async_gen
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.loop.run_until_complete(self.async_gen.__anext__())
        except StopAsyncIteration:
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.close()


def chat_knowledge_lib():
    # client = Client(api_key=DBGPT_API_KEY)
    client = Client(api_base=DBGPT_API_BASE, api_key=DBGPT_API_KEY)
    chat_completion = client.chat_stream(model=LLM_MODEL,
                                         messages="介绍下 杭州市闻涛小学",
                                         chat_mode=CHAT_MODEL,
                                         chat_param=SPACE_NAME)
    # async for data in chat_completion:
    #     print(data.choices[0].delta.content)
    response = ""
    for data in AsyncToSyncIterator(chat_completion):
        # print(data.choices[0].delta.content)
        response += data.choices[0].delta.content
    print(response)




# def main():
# loop = asyncio.get_event_loop()
# loop.run_until_complete(chat_knowledge_lib())


if __name__ == "__main__":
    chat_knowledge_lib()
