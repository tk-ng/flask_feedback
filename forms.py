from curses.ascii import EM
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired, Length, Email


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
                           Length(max=20), InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[
                        InputRequired(), Email(), Length(max=50)])
    first_name = StringField("First Name", validators=[
                             InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[
                            InputRequired(), Length(max=30)])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[
                           Length(max=20), InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[Length(max=100), InputRequired()])
    content = StringField("Content", validators=[InputRequired()])
