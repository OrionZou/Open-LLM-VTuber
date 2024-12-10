r""" Description: This file contains the implementation of the `ollama` class.
This class is responsible for handling the interaction with the OpenAI API for 
language generation.
And it is compatible with all of the OpenAI Compatible endpoints, including Ollama, 
OpenAI, and more.
"""

import json
import asyncio
from typing import Iterator
from queue import Queue
from dbgpt.client import Client
from llm.llm_interface import LLMInterface
# from .llm_interface import LLMInterface

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


class LLM(LLMInterface):

    def __init__(
        self,
        base_url: str,
        model: str,
        chat_model: str,
        callback=print,
        space_name: str = "z",
        llm_api_key: str = "z",
        verbose: bool = False,
    ):
        """
        Initializes an instance of the `ollama` class.

        Parameters:
        - base_url (str): The base URL for the OpenAI API.
        - model (str): The model to be used for language generation.
        - system (str): The system to be used for language generation.
        - callback [DEPRECATED] (function, optional): The callback function to be called after each API call. Defaults to `print`.
        - organization_id (str, optional): The organization ID for the OpenAI API. Defaults to an empty string.
        - project_id (str, optional): The project ID for the OpenAI API. Defaults to an empty string.
        - llm_api_key (str, optional): The API key for the OpenAI API. Defaults to an empty string.
        - verbose (bool, optional): Whether to enable verbose mode. Defaults to `False`.
        """

        self.base_url = base_url
        self.llm_api_key = llm_api_key
        self.model = model
        self.callback = callback
        self.verbose = verbose
        self.client = Client(
            api_base=base_url,
            api_key=llm_api_key,
        )
        self.chat_model = chat_model
        self.space_name = space_name

        # self.memory = Queue(maxsize=100)
        self.memory = []

    def chat_iter(self, prompt: str) -> Iterator[str]:

        # self.memory.put({
        #     "role": "user",
        #     "content": prompt,
        # })
        self.memory.append({
            "role": "user",
            "content": prompt,
        })
        # if self.verbose:
        #     self.__print_memory()
        #     print(" -- Base URL: " + self.base_url)
        #     print(" -- Model: " + self.model)
        #     print(" -- System: " + self.system)
        #     print(" -- Prompt: " + prompt + "\n\n")

        chat_completion = []
        try:
            chat_completion_itertor = AsyncToSyncIterator(
                self.client.chat_stream(model=self.model,
                                        messages=prompt,
                                        chat_mode=self.chat_model,
                                        chat_param=self.space_name,
                                        temperature=0.5))
            complete_response = ""
            for chunk in chat_completion_itertor:
                if len(chunk.choices[0].delta.content)>50:
                    break
                yield chunk.choices[0].delta.content
                complete_response += chunk.choices[0].delta.content
        except Exception as e:
            print("Error calling the chat endpoint: " + str(e))
            return "Error calling the chat endpoint: " + str(e)

        # self.memory.put({
        #     "role": "assistant",
        #     "content": complete_response,
        # })
        self.memory.append({
            "role": "assistant",
            "content": complete_response,
        })

        def serialize_memory(memory, filename):
            with open(filename, "w") as file:
                json.dump(memory, file)

        serialize_memory(self.memory, "mem.json")

    def handle_interrupt(self, heard_response: str) -> None:
        if self.memory[-1]["role"] == "assistant":
            self.memory[-1]["content"] = heard_response + "..."
        else:
            if heard_response:
                self.memory.append({
                    "role": "assistant",
                    "content": heard_response + "...",
                })
        self.memory.append({
            "role": "system",
            "content": "[Interrupted by user]",
        })


def test():
    DBGPT_API_BASE = "http://127.0.0.1:5670/api/v2"
    DBGPT_API_KEY = "dbgpt"
    LLM_MODEL = "/models/openbuddy"
    CHAT_MODEL = "chat_knowledge"
    SPACE_NAME = "edu_lib_v1"

    llm = LLM(
        base_url=DBGPT_API_BASE,
        model=LLM_MODEL,
        callback=print,
        llm_api_key=DBGPT_API_KEY,
        chat_model=CHAT_MODEL,
        space_name=SPACE_NAME,
    )
    while True:
        print("\n>> (Press Ctrl+C to exit.)")

        for chunk in llm.chat_iter(input(">> ")):
            if chunk:
                print(chunk, end="")


if __name__ == "__main__":
    test()
