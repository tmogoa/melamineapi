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
            error = "Email is required!"
        if not user.user_password:
            error = "Password is required!"
        
        if error is None:
            user.user_password = generate_password_hash(user.user_password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            abort(403, message=f"{e}")
        else:
            return user.user_id, 201

class LoginResource(Resource):
    def post(self):
        return self.login(request.get_json())
    def login(self, data):
        error = None
        user = UserSchema().load(data)

        a_user = User.query.filter_by(user_email=user.user_email).first()
        a_user_json = UserSchema().dump(a_user)
        if not a_user:
            error = "Invalid credentials!"
        elif not check_password_hash(a_user.user_password, user.user_password):
            error = "Invalid credentials!"
        
        if error is None:
            token = create_access_token(identity=str(a_user.user_id))
            response = jsonify({
                'user': a_user_json,
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
        return jsonify(msg="JWT revoked")
        response = jsonify({
            "msg": "Logout successful."
        })
        return response

