from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from data.user_model import User
from api.errors import AuthenticationErrors, RequestErrors
from datetime import timedelta
from api.schema.user_schema import UserSchema
from marshmallow import ValidationError
from api.utils.response_builder import error_response, success_response

admin_bp = Blueprint('admin', __name__)

@admin_bp.post('/delete')
@jwt_required()
def admin_delete_user():
    """
    Allows to delete any user in case the claimed role is 'admin'.

    body:
        'username': str, required, the user to delete
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.AUTH_REQUIRED)
        return error_response(error[0], error[1], 403)
    
    data = request.get_json()
    username = data.get('username')
    user = User.get_user_by_username(username)
    
    if not user:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID, exception='Username not found')
        return error_response(error[0], error[1], 404)
        
    user.delete()
    
    return success_response('User deleted successfully', status_code=200)

@admin_bp.get('/get-all')
@jwt_required()
def get_all_users():
    """
    Get a list of users
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.AUTH_REQUIRED)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 403
    
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=3, type=int)
    users = User.query.paginate(page=page, per_page=per_page)
    
    result = UserSchema().dump(users, many=True)
    
    return success_response('Users retrieved successfully', {'users': result}, status_code=200)