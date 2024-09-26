from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, BooleanField, TextAreaField, SubmitField, FloatField, FieldList, FormField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange
import sqlalchemy as sa
from app import db
from app.models import User, Company


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
    default_price = FloatField("Default Price (€)")
    submit = SubmitField("Submit")

class PackagePriceForm(FlaskForm):
    package_id = HiddenField("Package ID")  # Hidden field for package ID
    package_name = StringField("Package Name", render_kw={"readonly":True})  # Read-only field to display the package name
    price = FloatField('Price', validators=[NumberRange(min=0)], default="")

    class Meta:
        csrf = False

class NewCompanyForm(FlaskForm):
    name = StringField("Company Name", validators=[DataRequired()])
    contact = StringField("Contact email(s)", validators=[DataRequired()])
    address1 = StringField("Address Line 1", validators=[DataRequired()])
    address2 = StringField("Address Line 2 (Optional)")
    postcode = IntegerField("Postcode", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    notes = TextAreaField("Additional Notes")
    packages = FieldList(FormField(PackagePriceForm))
    submit = SubmitField("Submit")
        
class NewAssigneeForm(FlaskForm):
    name = StringField("Assignee Name", validators=[DataRequired()])
    origin_country = SelectField("Origin Country",
                                  validators=[DataRequired()])
    destination_city = SelectField("Destination City",
                                   validators=[DataRequired()], default="Berlin")
    company = SelectField("Company", validators=[DataRequired()])
    submit = SubmitField("Submit")
    # Need to add fields for packages!

    def __init__(self, *args, **kwargs):
        super(NewAssigneeForm, self).__init__(*args, **kwargs)
        # Query the database to get all company names and ids
        companies = db.session.execute(sa.select(Company.id, Company.name).order_by(Company.name)).all()
        # Set the choices for the company SelectField
        self.company.choices = [(company.id, company.name) for company in companies]