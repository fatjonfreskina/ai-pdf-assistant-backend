from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from flask_cors import CORS, cross_origin
from data.user_model import User
from utils.json_schemas import UserSchema
from api.errors import AuthenticationErrors, RequestErrors

users_bp = Blueprint('users', __name__)

@users_bp.post('/update-password')
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
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 404

    is_valid = User.validate_password(new_password)

    if not is_valid:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 400

    claims = get_jwt()
    claimed_username = claims.get('sub')
    user = User.get_user_by_username(claimed_username)
    
    if not user:
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.INVALID_USER)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 404
    
    user.set_password(new_password)
    user.save()
        
    return jsonify({
        'message': 'Password updated successfully',
    }), 200

@users_bp.post('/delete')
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
    
    return jsonify({
        'message': 'User deleted successfully',
    }), 200

### ADMIN ENDPOINTS ###
@users_bp.post('/admin/update-password')
@jwt_required
def admin_update_password():
    """
    Update user's passowrd

    body:
        'new_password': str, required
        'username' :    str, required, the user whose password will be changed
    """
    data = request.get_json()
    requested_username = data.get('username')
    new_password = data.get('new_password')

    if not new_password or not requested_username:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_FOUND)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 404

    is_new_password_valid = User.validate_password(new_password)
    if not is_new_password_valid:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 404

    claims = get_jwt()
    if claims.get('role') == 'admin' and is_new_password_valid:
        user = User.get_user_by_username(requested_username)
        if not user:
            error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID, 'User not found to update psw')
            return jsonify({
                'message': error[0],
                'error': error[1]
            }), 404
        user.set_password(new_password)
        user.save()
        return jsonify({
            'message': 'Password updated successfully',
        }), 200

@users_bp.post('/admin/delete')
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
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 403
    
    data = request.get_json()
    username = data.get('username')
    user = User.get_user_by_username(username)
    
    if not user:
        error = RequestErrors.get_error_instance(RequestErrors.BAD_REQUEST_BODY_NOT_VALID, exception='Username not found')
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 404
        
    user.delete()
    
    return jsonify({
        'message': 'User deleted successfully',
    }), 200

@users_bp.get('/admin/get-all')
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
    
    return jsonify({
        "users": result,
    }), 200


if __name__ == '__main__':
    print('test')