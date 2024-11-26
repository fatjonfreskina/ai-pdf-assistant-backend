from flask import Blueprint, jsonify, request, current_app, g
from data.user_model import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from flask_cors import CORS, cross_origin
from openai import OpenAI  # Version 1.33.0
from openai.types.beta.threads.message_create_params import Attachment, AttachmentToolFileSearch
import os
from api.errors import AiErrors
from werkzeug.utils import secure_filename
from api.utils.response_builder import error_response, success_response

"""
Documentation available here: https://platform.openai.com/docs/assistants/quickstart
"""

assistant_bp = Blueprint('ai', __name__)

@assistant_bp.before_request
def before_request():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    current_app.logger.info(f"Request from {ip}")
    g.MY_OPENAI_KEY = current_app.config.get('OPENAI_API_KEY')
    g.ALLOWED_EXTENSIONS = {'pdf'}
    g.UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER')
    g.client = OpenAI(api_key=g.MY_OPENAI_KEY)

@jwt_required()
@assistant_bp.get('/assistants')
def get_assistants():
    """Return a list of all the available assistants.
    """
    return jsonify({
        "assistants": [assistant.name for assistant in g.client.beta.assistants.list()]
    }), 200
    
@jwt_required()
@assistant_bp.get('/assistant/<assistant_name>')
def get_assistant_info(assistant_name: str):
    """Return the information of the assistant with the given name.
    """
    current_app.logger.info(f"Called get_assistant_info with assistant_name: {assistant_name}")
    assistant_instance = get_assistant_instance(assistant_name=assistant_name)
    if assistant_instance is None:
        error = AiErrors.get_error_instance(AiErrors.ASSISTANT_NOT_FOUND)
        return jsonify({
            "message": error[0],
            "error": error[1]
        }), 400
    return jsonify({
        "assistant": assistant_instance.to_dict()
    }), 200

@jwt_required()
@assistant_bp.post('/create-assistant')
def create_assistant():
    """Creates a new assistant with the given name, description, and instructions.
    
    body: {
        "name": "My Assistant Name",
        "description": "You are a PDF retrieval assistant.",
        "instructions": "You are a helpful assistant for service technicians. You can answer questions about the content of PDFs."
    }
    """
    new_assistant = request.get_json()
    current_app.logger.info(f"Called create_assistant with data: {new_assistant}")
    if new_assistant.get("name") not in [assistant.name for assistant in g.client.beta.assistants.list()]:
        g.client.beta.assistants.create(
            model="gpt-4o-mini",
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
        
@jwt_required()
@assistant_bp.post('/add-pdf')
def add_pdf_to_assistant():
    """Add a PDF file to the assistant's tool. Useful documentation here: https://platform.openai.com/docs/assistants/tools/file-search
    
    form-data: {
        "assistant_name": "My Assistant Name",
        "file": <file>
    }
    """
    # data = request.get_json()
    assistant_name = request.form.get('assistant_name')
    assistant_instance = get_assistant_instance(assistant_name=assistant_name)
    current_app.logger.info(f"Called add_pdf_to_assistant with assistant_name: {assistant_name}")
    
    if assistant_instance is None:
        error = AiErrors.get_error_instance(AiErrors.ASSISTANT_NOT_FOUND)
        return jsonify({
            "message": error[0],
            "error": error[1]
        }), 400
    
    if 'file' not in request.files:
        error = AiErrors.get_error_instance(AiErrors.FILE_NOT_FOUND)
        return jsonify({
            "message": error[0],
            "error": error[1]
        }), 400
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty part without a filename.
    if not file:
        error = AiErrors.get_error_instance(AiErrors.FILE_NOT_FOUND)
        return jsonify({
            "message": error[0],
            "error": error[1]
        }), 400
    
    if file.filename == '':
        error = AiErrors.get_error_instance(AiErrors.FILE_NOT_FOUND)
        return jsonify({
            "message": error[0],
            "error": error[1]
        }), 400
    
    if not allowed_file(file.filename):
        error = AiErrors.get_error_instance(AiErrors.FILENAME_NOT_ALLOWED)
        return jsonify({
            "message": error[0],
            "error": error[1]
        }), 400
    
    filename = secure_filename(file.filename)
    vector_store = g.client.beta.vector_stores.create(name=filename)
    target_folder = os.path.join(g.UPLOAD_FOLDER, assistant_name)
    os.makedirs(target_folder, exist_ok=True)  # Ensure the directory exists
    file_path = os.path.join(target_folder, filename)
    file.save(file_path)
    
    file_paths = [os.path.join(target_folder, file) for file in os.listdir(target_folder)]
    file_streams = [open(path, "rb") for path in file_paths]
    
    file_batch = g.client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    
    for stream in file_streams:
        stream.close()
    
    assistant = g.client.beta.assistants.update(
        assistant_id=assistant_instance.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
        
    return jsonify({
        "message": "File uploaded successfully."
    }), 201
    
@jwt_required()
@assistant_bp.post('/ask')
def ask_question():
    """Ask a question to the assistant and return the response.
    
    body: {
        "question": "What does the High Inverter Temperature error mean in the TT series Danfoss Turbocor compressors mean? How can I assess the issue?",
        "assistant_name": "My Assistant Name"
    """
    try:
        data = request.get_json()
        question = data.get('question')
        assistant_name = data.get('assistant_name')
        current_app.logger.info(f"Called ask_question with question: {question} and assistant_name: {assistant_name}")

        # Create a new thread
        thread = g.client.beta.threads.create()

        # Send the question to the assistant
        g.client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=question,
        )

        # Run the thread and wait for the response
        run = g.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=get_assistant_instance(assistant_name=assistant_name).id,
            timeout=60,
        )

        # Retrieve the failure details
        if run.status == "failed":
            run = g.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            failure_error = run.last_error.code + " - " + run.last_error.message
            current_app.logger.error(f"Run failed with error: {failure_error}")
            
        # Check if the run was successful
        if run.status != "completed":
            current_app.logger.error(f"Run failed with status: {run.status}")
            error = AiErrors.get_error_instance(AiErrors.CLIENT_RUN_FAIL)
            return jsonify({
                "message": error[0],
                "error": error[1]
                }), 500

        # Fetch the response message
        messages_cursor = g.client.beta.threads.messages.list(thread_id=thread.id)
        messages = [message for message in messages_cursor]

        # Extract the assistant's response
        message = messages[0]
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(annotation.text, f' [{index}]')
            # Gather citations based on annotation attributes
            if (file_citation := getattr(annotation, 'file_citation', None)):
                cited_file = g.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] from {cited_file.filename}")
                # Quotes would be amazing. Although they seem to be removed from the API: 
                # https://github.com/openai/openai-openapi/issues/263

        # Return the response
        return jsonify({
            "response": message_content.value,
            "citations": citations})

    except Exception as e:
        error = AiErrors.get_error_instance(AiErrors.UNHANDLED_EXCEPTION, str(e))
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 500
    
# Utility functions
def get_assistant_instance(assistant_name: str):
    for assistant in g.client.beta.assistants.list():
        if assistant.name == assistant_name:
            return assistant

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in g.ALLOWED_EXTENSIONS