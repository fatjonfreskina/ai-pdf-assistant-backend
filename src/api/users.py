from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from flask_cors import CORS, cross_origin
from data.user_model import User
from utils.json_schemas import UserSchema

users_bp = Blueprint('users', __name__)

@users_bp.get('/all')
@jwt_required()
def get_all_users():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'You are not authorized to access this resource',
            'error': 'unauthorized'
        }), 403
    
    page = request.args.get(
        'page', 
        default=1, 
        type=int
    )
    
    per_page = request.args.get(
        'per_page', 
        default=3, 
        type=int
    )
    
    users = User.query.paginate(
        page=page,
        per_page=per_page,
    )
    
    result = UserSchema().dump(users, many=True)
    
    return jsonify({
        "users": result,
    }), 200
    
@users_bp.post('/delete')
@jwt_required()
def delete_user():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({
            'message': 'You are not authorized to access this resource',
            'error': 'unauthorized'
        }), 403
    
    username = request.args.get('username')
    user = User.get_user_by_username(username)
    
    if not user:
        return jsonify({
            'message': 'User not found',
            'error': 'not_found'
        }), 404
        
    user.delete()
    
    return jsonify({
        'message': 'User deleted successfully',
    }), 200
    
@users_bp.post('/update-password')
@jwt_required()
def update_password():
    data = request.get_json()
    requested_username = data.get(
        'username', 
        None
    )
    claims = get_jwt()
    new_password = request.json.get('new_password')
    
    # Admin can update any user's password
    if requested_username and claims.get('role') == 'admin':
        user = User.get_user_by_username(requested_username)
        
        if not user:
            return jsonify({
                'message': 'User not found',
                'error': 'not_found'
            }), 404
            
        user.set_password(new_password)
        user.save()
        return jsonify({
            'message': 'Password updated successfully',
        }), 200
    
    # User can update his/her password
    claimed_username = claims.get('sub')
    user = User.get_user_by_username(claimed_username)
    
    if not user:
        return jsonify({
            'message': 'User not found',
            'error': 'not_found'
        }), 404
    
    user.set_password(new_password)
    user.save()
        
    return jsonify({
        'message': 'Password updated successfully',
    }), 200