from flask import request, jsonify
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt
)
from datetime import datetime, timezone


from api.db.database import db
from api.models.user import User
from api.models.tokenblocklist import TokenBlocklist
from api.schemas.user_schema import UserSchema

USERS_ENDPOINT = "/api/users"

class RegisterResource(Resource): 
    def post(self):
        return self.register(request.get_json())
        
    def register(self, data):
        error = None
        user  = UserSchema().load(data)

        if not user.user_email:
            error = "EMAIL_REQUIRED"
        if not user.user_password:
            error = "PASSWORD_REQUIRED"
        
        if error is None:
            user.user_password = generate_password_hash(user.user_password)
        else:
            abort(403, message=f"{error}")
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            abort(403, message=f"EMAIL_TAKEN")
        else:
            user_json = UserSchema().dump(user)
            token = create_access_token(identity=str(user.user_id))
            response = jsonify({
                'user_id': user_json["user_id"],
                'user_email':  user_json["user_email"],
                'token': token
            })
            return response

class LoginResource(Resource):
    def post(self):
        return self.login(request.get_json())
    def login(self, data):
        error = None
        user = UserSchema().load(data)

        a_user = User.query.filter_by(user_email=user.user_email).first()
        a_user_json = UserSchema().dump(a_user)
        if not a_user:
            error = "INVALID_CREDS"
        elif not check_password_hash(a_user.user_password, user.user_password):
            error = "INVALID_CREDS"
        
        if error is None:
            token = create_access_token(identity=str(a_user.user_id))
            response = jsonify({
                'user_id': a_user_json["user_id"],
                'user_email': a_user_json["user_email"],
                'token': token
            })
            return response
        else:
            abort(401, message=f'{error}')

class LogoutResource(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        db.session.add(TokenBlocklist(jti=jti, created_at=now))
        db.session.commit()
        return jsonify(message="JWT_REVOKED")

