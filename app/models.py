from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return user.query.get(user_id)
class user(db.Model, UserMixin):
    id=db.Column(db.Integer(), primary_key=True)
    first_name=db.Column(db.String(12), nullable=False)
    last_name=db.Column(db.String(8), nullable=False)
    username=db.Column(db.String(8), unique=True, nullable=False)
    email=db.Column(db.String(), unique=True, nullable=False)
    password=db.Column(db.String(8), nullable=False)
    date=db.Column(db.DateTime())
    profile_img=db.Column(db.String(), nullable=False, default="default.png")
    bio=db.Column(db.Text(), nullable=True)

    def __repr__(self):
        return f"{self.first_name[:3]}-{self.id}"