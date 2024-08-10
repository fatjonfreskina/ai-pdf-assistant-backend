from flask import Blueprint, jsonify, request
from data.user_model import User
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_cors import CORS, cross_origin

auth_bp = Blueprint('auth', __name__)

@auth_bp.post('/register')
def register():
    data = request.get_json()
    user = User.get_user_by_username(data['username'])
    if user:
        return jsonify({'message': 'Username already taken!'}), 400
    
    new_user = User(
        username = data['username'], 
        email = data['email'],
    )
    
    new_user.set_password(data['password'])
    new_user.save()
    
    return jsonify({
        'message': 'User created successfully!'
    }), 400

@auth_bp.post('/login')
@cross_origin()
def login_user():
    data = request.get_json()
    user = User.get_user_by_username(data['username'])
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 400
    
    return jsonify({
        'message': 'Login successful!',
        'tokens': {
            'access_token': create_access_token(identity=user.id),
            'refresh_token': create_refresh_token(identity=user.id)
        },
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200
    
    
    
# user = User.query.filter_by(id=get_jwt_identity()).first()