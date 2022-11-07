from marshmallow import Schema, fields, post_load
from api.models.lesion import Lesion
from api.schemas.user_schema import UserSchema

class LesionSchema(Schema):
    lesion_id = fields.Integer()
    user_id = fields.Integer()
    user = fields.Nested(UserSchema(), dump_only=True)
    lesion_img_url = fields.String(allow_none=False)
    lesion_malignancy = fields.Integer()
    lesion_pred_conf = fields.Float(allow_nan=False)
    lesion_timestamp = fields.DateTime()

    @post_load
    def make_lesion(self, data, **kwargs):
        return Lesion(**data)
