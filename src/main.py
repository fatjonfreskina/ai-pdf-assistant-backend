from flask import Flask, request, jsonify
from data.extensions import db, jwt
from api.auth import auth_bp
from api.users import users_bp
from api.assistant import assistant_bp
from flask_cors import CORS, cross_origin
from flask_jwt_extended import jwt_required, get_jwt
from data.user_model import User
from api.errors import AuthenticationErrors
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from logging.config import dictConfig

load_dotenv()

def create_app():
    # Set up logging
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    
    app = Flask(__name__)   
    app.config.from_prefixed_env()
            
    if os.getenv('ENVIRONMENT') == 'production':
        app.config['UPLOAD_FOLDER'] = '/media'
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_PROD')
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    else:
        app.config['UPLOAD_FOLDER'] = 'uploads'
        SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI_DEV')
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        app.config['CORS_HEADERS'] = 'Content-Type'
        
    app.logger.info(f'Running in {os.getenv("ENVIRONMENT")} mode')
    
    cors = CORS(app)
    db.init_app(app)
    with app.app_context():
        app.logger.info('Creating all tables')
        db.create_all()
    jwt.init_app(app)
    
    # Register the blueprints  
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(assistant_bp, url_prefix='/ai')
    
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
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.TOKEN_EXPIRED)
        return jsonify({
            'message':  error[0],
            'error':    error[1]
        }), 401
    
    @jwt.invalid_token_loader
    def my_invalid_token_callback(error):
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.INVALID_TOKEN)
        return jsonify({
            'message': error[0],
            'error': error[1]
        }), 401
        
    @jwt.unauthorized_loader
    def my_unauthorized_loader(error):
        error = AuthenticationErrors.get_error_instance(AuthenticationErrors.AUTH_REQUIRED)
        return jsonify({
            'message': error[0],
            'error': error[1] 
        }), 401
    return app