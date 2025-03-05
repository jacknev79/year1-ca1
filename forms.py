from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, IntegerField

from wtforms.validators import InputRequired, EqualTo

class RegistrationForm(FlaskForm):
    user_id = StringField('User id:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    password2 = PasswordField('Please re-enter your password:',
                              validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField()

class LoginForm(FlaskForm):
    user_id = StringField("User_id:", validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField()

class RequestForm(FlaskForm):
    book_id = StringField('ID of any other book you wish to request:', validators=[InputRequired()])
    submit = SubmitField()

class AdminForm(FlaskForm):
    admin_id = StringField('Admin Login:')
    admin_password = PasswordField('Password: ')

class AddBookForm(FlaskForm):
    title = StringField('Title:', validators=[InputRequired()])
    author = StringField('Author:', validators=[InputRequired()])
    dewey_decimal = StringField('Location in DDS:', validators=[InputRequired()])
    genre = StringField('Genre', validators=[InputRequired()])
    location = StringField('Floor located on:', validators=[InputRequired()])
    checked_out = BooleanField('If book checked out:', render_kw={'value': '1'})
    restricted= BooleanField('If book restricted:', render_kw={'value': '1'}, validators=[])
    description = StringField('Short description of book:')
    user_id = StringField('User ID of person checking book out:')
    submit = SubmitField()

class RemoveBookForm(FlaskForm):
    book_id = IntegerField('ID of book to be removed:')
    book_id2 = IntegerField('Please re-enter book ID:', validators=[EqualTo('book_id')])
    submit = SubmitField()

class CheckoutForm(FlaskForm):
    submit = SubmitField('Checkout')


