from app.models import user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import EqualTo, Email, Length, DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from app import bcrypt


class Sign_Up_Form(FlaskForm):
    def validate_username(self, username_to_check):
        username_check = user.query.filter_by(username=username_to_check.data).first()
        if username_check:
            raise ValidationError("Username is already being used!")
    def validate_email(self, email_to_check):
        email_check = user.query.filter_by(email=email_to_check.data).first()
        if email_check:
            raise ValidationError("Username is already being used!")
    
    first_name=StringField(label="First Name", validators=[Length(min=3, max=12), DataRequired()])
    last_name=StringField(label="Last Name", validators=[Length(min=3, max=8), DataRequired()])
    username=StringField(label="Username", validators=[Length(min=3, max=8), DataRequired()])
    email=StringField(label="Email", validators=[Email(), DataRequired()])
    password=PasswordField(label="Password", validators=[Length(min=8), DataRequired()])
    confirm_password=PasswordField(label="Confirm Password", validators=[EqualTo('password'), DataRequired()])
    img=FileField(label="Select Image", validators=[FileAllowed(['jpg', 'png', 'jpeg'], FileRequired())])
    submit=SubmitField(label="Join Now")

class Sign_In_Form(FlaskForm):
    username=StringField(label="Username", validators=[DataRequired()])
    password=PasswordField(label="Password", validators=[DataRequired()])
    submit=SubmitField(label="Sign In")

class Image_Form(FlaskForm):
    img=FileField(label="Select Image", validators=[FileAllowed(['jpg', 'png', 'jpeg']), FileRequired()])

class Change_Pass_Form(FlaskForm):
    old_password=PasswordField(label="Password", validators=[Length(min=8), DataRequired()])
    new_password=PasswordField(label="New Password", validators=[Length(min=8), DataRequired()])
    confirm_password=PasswordField(label="Confirm New Password", validators=[EqualTo('new_password'), DataRequired()])
    change_password=SubmitField(label="Change Password")
