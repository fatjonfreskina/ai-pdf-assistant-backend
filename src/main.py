from flask import Flask, request, jsonify
from data.extensions import db, jwt
from api.auth import auth_bp
from api.users import users_bp
from api.ai_pdf_assistant import ai_pdf_assistant_bp
from flask_cors import CORS, cross_origin
from flask_jwt_extended import jwt_required, get_jwt
from data.user_model import User
from api.errors import AuthenticationErrors

# TODO: Move extensions in another place

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config['UPLOAD_FOLDER'] = 'uploads'
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


@auth_bp.get('/whoami')
@jwt_required()
def whoami():
    claims = get_jwt()
    return jsonify( { 'message': 'You are authenticated', 'claims': claims } )