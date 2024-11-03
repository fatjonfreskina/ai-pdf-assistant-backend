from flask_jwt_extended import jwt_required, get_jwt, create_access_token, create_refresh_token
from flask_cors import CORS, cross_origin
from data.user_model import User
from api.errors import AuthenticationErrors, RequestErrors
from flask import Blueprint, jsonify, request, current_app
from datetime import timedelta
from api.schema.registration_schema import RegistrationSchema
from marshmallow import ValidationError
from api.utils.response_builder import error_response, success_response

user_bp = Blueprint('user', __name__)

@user_bp.post('/register')
@cross_origin()
def register():
    data = request.get_json()
    registration_schema = RegistrationSchema()
    try:
        validation_result = registration_schema.load(data)
    except ValidationError as err:        
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID)
        return error_response(err.messages, error[1])
    
    new_username = validation_result['username']
    email = validation_result['email']
    password = validation_result['password']

    if User.get_user_by_username(new_username):
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.USERNAME_ALREADY_TAKEN)
        return error_response(error[0], error[1])


    if User.get_user_by_email(email):
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.EMAIL_ALREADY_TAKEN)
        return error_response(error[0], error[1])

    is_password_valid = User.validate_password(password)
    if not is_password_valid:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID)
        return error_response(error[0], error[1])

    try:
        new_user = User(username = new_username, email = email)
        new_user.set_password(password)
        new_user.save()
    except Exception as e:
        current_app.logger.error(f"Error creating user: {str(e)}")
        error = RequestErrors.get_error_instance(RequestErrors.INTERNAL_SERVER_ERROR)
        return error_response("An error occurred while creating the user", error[1], status_code=500)
    return success_response('User created successfully!')

@user_bp.post('/login')
@cross_origin()
def login_user():
    data = request.get_json()
    username = data.get('username')
    current_app.logger.info(f"Called login with username: {username}")
    user = User.get_user_by_username(username)
    if not user or not user.check_password(data['password']):
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.LOGIN_FAILED)
        return error_response(error[0], error[1])
    
    return jsonify({
        'message': 'Login successful!',
        'tokens': {
            'access_token': create_access_token(identity=user.username, expires_delta=timedelta(days=7)),
            'refresh_token': create_refresh_token(identity=user.username)
        },
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200

@user_bp.post('/update-password')
@jwt_required()
def update_password():
    """
    Update user's passowrd

    body:
        'new_password': str, required
    """
    data = request.get_json()
    new_password = data.get('new_password')

    if not new_password:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_FOUND)
        return error_response(error[0], error[1])

    is_valid = User.validate_password(new_password)

    if not is_valid:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID)
        return error_response(error[0], error[1])

    claims = get_jwt()
    claimed_username = claims.get('sub')
    user = User.get_user_by_username(claimed_username)
    
    if not user:
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.INVALID_USER)
        return error_response(error[0], error[1])
    
    user.set_password(new_password)
    user.save()
        
    return success_response('Password updated successfully!')

@user_bp.post('/delete')
@jwt_required()
def delete_user():
    """
    Allows to delete the user associated to the claimed identity (jwt).

    body: None
    """
    claims = get_jwt()
    username = claims.get('sub')
    user = User.get_user_by_username(username)
    
    if not user:
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.INVALID_USER)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 404
        
    user.delete()
    
    return success_response('User deleted successfully!')


