from flask import Flask, request, jsonify
from data.extensions import db, jwt
from api.auth import auth_bp
from api.users import users_bp
from api.ai_pdf_assistant import ai_pdf_assistant_bp
from flask_cors import CORS, cross_origin
import logging
from flask_jwt_extended import jwt_required, get_jwt
from data.user_model import User

# TODO: Move extensions in another place
# TODO: Fix the sha256 in db

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    cors = CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    
    # Register the blueprints  
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(ai_pdf_assistant_bp, url_prefix='/ai')
    
    # Additional claims loader 
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        if identity == 'fatjonfreskina':
            return { 'role': 'admin' }
        return { 'role': 'user'}
    
    # User loader
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_headers, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(username=identity).one_or_none()
    
    # Error handling 
    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_data):
        return jsonify({
            'message': 'The token has expired',
            'error': 'token_expired' 
        }), 401
    
    @jwt.invalid_token_loader
    def my_invalid_token_callback(error):
        return jsonify({
            'message': 'Signature verification failed',
            'error': 'invalid_token' 
        }), 401
        
    @jwt.unauthorized_loader
    def my_unauthorized_loader(error):
        return jsonify({
            'message': 'Missing Authorization Header',
            'error': 'authorization_required' 
        }), 401
    return app


@auth_bp.get('/whoami')
@jwt_required()
def whoami():
    claims = get_jwt()
    return jsonify( { 'message': 'You are authenticated', 'claims': claims } )