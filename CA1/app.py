from flask import Flask, render_template, session, redirect, url_for, g, request
from flask_session import Session
from forms import LoginForm, RegistrationForm
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LKmfRPwipKUmgzbrYYHYLCdf'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.teardown_appcontext(close_db)

Session(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get('user_id', None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

@app.route('/')
def index():


    return render_template('index.html')

@app.route('/library')
def library():
    db = get_db()
    books = db.execute('''SELECT * FROM books;''').fetchall()

    return render_template('books.html', books=books)

@app.route('/library/<int:book_id>')
def library(book_id):
    db = get_db()
    book = db.execute('''SELECT * FROM books
                      WHERE book_id = ?;''', (book_id,)).fetchone()

    return render_template

@app.route('/cart')
@login_required
def cart():
    if 'cart' not in session:
        session['cart'] = {}
        session.modified = True

    names = {}
    db = get_db()
    for book_id in session['cart']:
        book = db.execute('''SELECT * FROM books
                          WHERE book_id = ?''', (book_id,)).fetchone()
        name = book['title']
        names[book_id] = name
    return render_template()

#might delete quantity???
@app.route('/add_to_cart/<int:book_id>/<int:qnt>')
@login_required
def add_to_cart(book_id ,qnt):
    if 'cart' not in session:
        session['cart'] = {}
    if book_id not in session['cart']:
        session['cart'][book_id] = qnt

    else: 
        session['cart'][book_id] = session['cart'][book_id] + qnt

    session.modified = True
    return render_template()

@app.route('/register', methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        clash = db.execute('''SELECT * FROM users
                           WHERE user_id = ?;''', (user_id,)).fetchone()
        
        if clash is not None:
            form.user_id.errors.append('User name is already taken.')
        else:
            register_date = date.now().strftime('%y-%m-%d')
            db.execute('''INSERT INTO users
                       VALUES (?,?,?,0);''',(user_id, generate_password_hash(password),register_date))
            db.commit()
            return redirect( url_for('login'))
        
        return render_template('register.html', form=form)
    
@app.route('/login', methods = ["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        db = get_db()
        user_in_db = db.execute('''SELECT user_id, password FROM users
                                WHERE user_id = ?;''',(user_id,)).fetchone()
        
        if user_in_db is None:
            form.user_id.errors.append('Username does not exist.')

        elif not check_password_hash(user_in_db['password'], password):
            form.password.errors.append('Incorrect password.')

        else:
            session.clear()
            session['user_id'] = user_id
            session.modified = True
            next_page = request.args.get('next')
            if not next_page:
                next_page = url_for('index')
            return redirect(next_page)
        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return redirect(url_for("index"))

@app.route('/history')
@login_required
def history():
    current_date = date.now().strftime('%y-%m-%d')
    db = get_db()
    books = db.execute('''SELECT * FROM books 
                       WHERE book_id = (SELECT book_id FROM checkout
               WHERE user_id = ? AND date_returned < ?);''',(
                   session['user_id'], current_date)).fetchall()
    return render_template #library page/ table

@app.route('/checked_out')
@login_required
def checked_out():
    
    db = get_db()
    books = db.execute('''SELECT * FROM books 
                       WHERE book_id = (SELECT book_id FROM checkout
                       WHERE user_id = ? AND date_returned IS NULL);''',(session['user'], None)).fetchall()
    return render_template()