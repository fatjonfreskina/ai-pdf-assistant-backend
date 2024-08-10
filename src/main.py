from flask import Flask, request, jsonify
from data.extensions import db, jwt
from api.auth import auth_bp
from api.users import users_bp
from api.ai_pdf_assistant import ai_pdf_assistant_bp
from flask_cors import CORS, cross_origin

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
    
    return app