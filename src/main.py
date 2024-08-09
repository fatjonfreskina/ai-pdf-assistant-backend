from flask import Flask, request, jsonify
from data.extensions import db, jwt
from api.auth import auth_bp
from api.users import users_bp

# TODO: Move extensions in another place
# TODO: Fix the sha256 in db

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    db.init_app(app)
    jwt.init_app(app)
    
    # Register the blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    
    return app