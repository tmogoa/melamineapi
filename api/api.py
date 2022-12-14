import logging
import sys
import os
from datetime import timedelta

from flask import Flask, url_for
from flask_restful import Api
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from api.db.database import db, init_db

from api.models.tokenblocklist import TokenBlocklist
from api.resources.users_resource import (
    RegisterResource,
    LoginResource,
    LogoutResource,
    USERS_ENDPOINT
)
from api.resources.lesions_resource import(
    LesionsResource,
    LESIONS_ENDPOINT
)

load_dotenv()

def create_app():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
        handlers=[logging.FileHandler("melamineapi.log"), logging.StreamHandler()],
    )

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'melamine.sqlite'),
    )
    ACCESS_EXPIRES = timedelta(hours=24)
    app.config["JWT_COOKIE_SECURE"] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_db(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.config['DATABASE']}"

    db.init_app(app)

    api = Api(app)
    jwt = JWTManager(app)
    CORS(app, expose_headers='Authorization')
    api.add_resource(RegisterResource, f"{USERS_ENDPOINT}/signup")
    api.add_resource(LoginResource, f"{USERS_ENDPOINT}/login")
    api.add_resource(LogoutResource, f"{USERS_ENDPOINT}/logout")
    api.add_resource(
        LesionsResource, 
        f"{LESIONS_ENDPOINT}", 
        f"{LESIONS_ENDPOINT}/<id>", 
        f"{LESIONS_ENDPOINT}/<id>/<lesion_id>"
    )

    # Callback function to check if a JWT exists in the database blocklist
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None

    return app