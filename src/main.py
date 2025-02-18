from flask import Flask, request, jsonify
from data.extensions import db, jwt
from api.admin import admin_bp
from api.user import user_bp
from api.assistant import assistant_bp
from flask_cors import CORS
from flask_jwt_extended import jwt_required, get_jwt
from data.user_model import User
from api.errors import AuthenticationErrors
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from logging.config import dictConfig
from itsdangerous import URLSafeTimedSerializer

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
    allowed_origin = app.config.get('ALLOWED_ORIGIN')
    if allowed_origin:
        cors = CORS(app, resources={r"/api/*": {"origins": allowed_origin}})
            
    if os.getenv('ENVIRONMENT') == 'production':
        app.config['UPLOAD_FOLDER'] = '/media'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI_PROD')
        app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL_PROD')
        app.config['EMAIL_SERVICE_URL'] = os.getenv('EMAIL_SERVICE_URL_PROD')
        app.logger.info(f'Running in production mode')
    else:
        app.config['UPLOAD_FOLDER'] = 'uploads'
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI_DEV')
        app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL_DEV')
        app.config['EMAIL_SERVICE_URL'] = os.getenv('EMAIL_SERVICE_URL_DEV')
        app.logger.info(f'Running in development mode')
        
    app.config['HASH_SALT'] = os.getenv('HASH_SALT')
    app.config['EMAIL_SERVICE_API_KEY'] = os.getenv('EMAIL_SERVICE_API_KEY')
    app.config['SUDO_PASSWORD'] = os.getenv('SUDO_PASSWORD')
    
    cors = CORS(app)
    db.init_app(app)
    with app.app_context():
        app.logger.info('Creating all tables')
        db.create_all()
    jwt.init_app(app)
    
    # Register the blueprints  
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(assistant_bp, url_prefix='/ai')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    app.config['SERIALIZER'] = serializer
    
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