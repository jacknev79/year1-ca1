from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, RadioField

from wtforms.validators import InputRequired, EqualTo

class RegistrationForm(FlaskForm):
    user_id = StringField('User id:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    password2 = PasswordField('Please re-enter your password:',
                              validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField()

class LoginForm(FlaskForm):
    user_id = StringField("User_id:", validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField()




