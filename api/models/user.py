from api.db.database import db

class User(db.Model):
    
    #__tablename__ = ""
    user_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_email = db.Column(
        db.String(),
        nullable=False
    )
    user_password = db.Column(
        db.String(),
        nullable=False
    )