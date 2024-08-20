from flask import Blueprint, jsonify, request
from data.user_model import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from flask_cors import CORS, cross_origin
from openai import OpenAI  # Version 1.33.0
from openai.types.beta.threads.message_create_params import Attachment, AttachmentToolFileSearch
import os
from dotenv import load_dotenv
from api.errors import AiErrors

"""
Documentation available here: https://platform.openai.com/docs/assistants/quickstart
"""

ai_pdf_assistant_bp = Blueprint('ai', __name__)
load_dotenv()
MY_OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=MY_OPENAI_KEY)

# TEST: OK
@jwt_required()
@ai_pdf_assistant_bp.get('/assistants')
def get_assistants():
    """Return a list of all the available assistants.
    """
    return jsonify({
        "assistants": [assistant.name for assistant in client.beta.assistants.list()]
    }), 200
    

# TEST: OK
@jwt_required()
@ai_pdf_assistant_bp.post('/create-assistant')
def create_assistant():
    """Creates a new assistant with the given name, description, and instructions.
    """
    new_assistant = request.get_json()
    if new_assistant.get("name") not in [assistant.name for assistant in client.beta.assistants.list()]:
        client.beta.assistants.create(
            model="gpt-4o",
            description=new_assistant.get("description"),
            instructions=new_assistant.get("instructions"),
            tools=[{"type": "file_search"}],
            name=new_assistant.get("name"),
        )
        return jsonify({
            "message": "Assistant created successfully."
        }), 201
    else:
        return jsonify({
            "message": "Assistant already exists."
        }), 400


# TEST: OK
@jwt_required()
@ai_pdf_assistant_bp.post('/ask')
def ask_question():
    """Ask a question to the assistant and return the response.
    """
    try:
        data = request.get_json()
        question = data.get('question')
        assistant_name = data.get('assistant_name')

        # Create a new thread
        thread = client.beta.threads.create()

        # Send the question to the assistant
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=question,
        )

        # Run the thread and wait for the response
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=get_assistant_instance(assistant_name=assistant_name).id,
            timeout=60,
        )

        # Check if the run was successful
        if run.status != "completed":
            error = AiErrors.get_error_instance(AiErrors.CLIENT_RUN_FAIL)
            return jsonify({
                "message": error[0],
                "error": error[1]
                }), 500

        # Fetch the response message
        messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
        messages = [message for message in messages_cursor]

        # Extract the assistant's response
        message = messages[0]
        response_text = message.content[0].text.value

        # Return the response
        return jsonify({"response": response_text})

    except Exception as e:
        error = AiErrors.get_error_instance(AiErrors.UNHANDLED_EXCEPTION, str(e))
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 500
    

# TEST: TODO 
def get_assistant_instance(assistant_name: str):
    for assistant in client.beta.assistants.list():
        if assistant.name == assistant_name:
            return assistant
    