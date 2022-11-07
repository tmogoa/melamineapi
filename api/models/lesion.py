from api.db.database import db
from datetime import datetime

class Lesion(db.Model):

    lesion_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.user_id"),
        nullable=False
    )
    lesion_img_url = db.Column(
        db.String(),
        nullable=False
    )
    lesion_malignancy = db.Column(
        db.Integer,
        nullable=False
    )
    lesion_pred_conf = db.Column(
        db.Float,
        nullable=False
    )
    lesion_timestamp = db.Column(
        db.TIMESTAMP,
        nullable=False,
        default=datetime.now()
    )