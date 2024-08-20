from flask import Blueprint, jsonify, request
from data.user_model import User
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_cors import CORS, cross_origin
from datetime import timedelta
from api.errors import RequestErrors, AuthenticationErrors

auth_bp = Blueprint('auth', __name__)

# TODO: TEST
@auth_bp.post('/register')
def register():
    """
    Sign up a new user.

    body:
        'username': str, required
        'email':    str, required 
        'password': str, required
    """
    data = request.get_json()
    new_username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not new_username or not email or not password:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_FOUND)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 400

    user = User.get_user_by_username(new_username)
    if user:
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.USERNAME_ALREADY_TAKEN)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 400

    user_with_existing_email = User.get_user_by_email(email)
    if user_with_existing_email:
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.EMAIL_ALREADY_TAKEN)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 400

    new_user = User(username = new_username, email = email)
    is_password_valid = User.validate_password(password)
    if not is_password_valid:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 400

    new_user.set_password(password)
    new_user.save()
    
    return jsonify({
        'message': 'User created successfully!'
    }), 200

@auth_bp.post('/login')
@cross_origin()
def login_user():
    data = request.get_json()
    username = data.get('username')
    user = User.get_user_by_username(username)
    if not user or not user.check_password(data['password']):
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.LOGIN_FAILED)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 400
    
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
    
# user = User.query.filter_by(id=get_jwt_identity()).first()