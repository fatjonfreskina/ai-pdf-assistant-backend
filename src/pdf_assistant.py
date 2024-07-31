from openai import OpenAI
import os
import sys
import time
from typing import List, Optional

class PDFAssistant:
    """
    A class to interact with the OpenAI API to create an assistant for answering questions based on a PDF file.

    Attributes:
        client (OpenAI): Client for interacting with OpenAI API.
        assistant_id (Optional[str]): ID of the created assistant. None until an assistant is created.
    """
    def __init__(self, api_key: str) -> None:
        """
        Initializes the PDFAssistant with the API key from environment variables.
        """
        if api_key is None:
            raise ValueError("API Key not found in environment variables")
        self.client = OpenAI(api_key=api_key)
        self.assistant_id: Optional[str] = None

    def upload_file(self, filename: str) -> None:
        """
        Uploads a file to the OpenAI API and creates an assistant related to that file.

        Args:
            filename (str): The path to the file to be uploaded.
        """
        file = self.client.files.create(
            file=open(filename, 'rb'),
            purpose="assistants"
        )

        assistant = self.client.beta.assistants.create(
            name="PDF Helper",
            description="You are a PDF retrieval assistant.",
            instructions="You are a helpful assistant designed to output only JSON. Find information from the text and files provided.",
            tools=[{"type": "file_search"}],
            model="gpt-4o",
            tool_resources={
                "code_interpreter": {
                "file_ids": [file.id]
                }
            }
        )
        self.assistant_id = assistant.id

    def get_answers(self, question: str) -> List[str]:
        """
        Asks a question to the assistant and retrieves the answers.

        Args:
            question (str): The question to be asked to the assistant.

        Returns:
            List[str]: A list of answers from the assistant.

        Raises:
            ValueError: If the assistant has not been created yet.
        """
        if self.assistant_id is None:
            raise ValueError("Assistant not created. Please upload a file first.")

        thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id
        )

        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            time.sleep(10)
            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(thread_id=thread.id)
                break
            else:
                time.sleep(2)

        return [message.content[0].text.value for message in messages.data if message.role == "assistant"]
            