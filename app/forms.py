from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different userneme")
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User). where(
            User.email == email.data))
        if user is not None:
            raise ValidationError("Please use a different email address")
        
class NewPackageForm(FlaskForm):
    name = StringField("Package Name", validators=[DataRequired()])
    description = StringField("Description (optional)")
    submit = SubmitField("Submit")

class NewCompanyForm(FlaskForm):
    name = StringField("Company Name", validators=[DataRequired()])
    contact = StringField("Contact email(s)", validators=[DataRequired()])
    notes = TextAreaField("Additional Notes")
    # need to add prices per package
    submit = SubmitField("Submit")
        
class NewAssigneeForm(FlaskForm):
    name = StringField("Assignee Name", validators=[DataRequired()])
    origin_country = StringField("Origin Country", validators=[DataRequired()])
    destination_city = StringField("Destination City", validators=[DataRequired()], default="Berlin")
    company = StringField("Company", validators=[DataRequired()])
    submit = SubmitField("Submit")
    # Need to add fields for packages!