from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, RadioField, DateField
from wtforms.validators import DataRequired


# WTForm
class TodoForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    due_date = DateField("Due Date")
    status = RadioField('Completed', choices=['Complete', 'Open'], default='Open')
    submit = SubmitField("Create Task")


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let me in")
