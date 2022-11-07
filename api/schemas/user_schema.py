from marshmallow import Schema, fields, post_load
from api.models.user import User

class UserSchema(Schema):
    user_id = fields.Integer()
    user_email = fields.String(allow_none=False)
    user_password = fields.String(allow_none=False)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)