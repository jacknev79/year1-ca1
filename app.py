from flask import Flask, render_template, session, redirect, url_for, g, request
from flask_session import Session
from forms import LoginForm, RegistrationForm, RequestForm, AdminForm, AddBookForm, RemoveBookForm, CheckoutForm
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
def book(book_id):
    db = get_db()
    book = db.execute('''SELECT * FROM books
                      WHERE book_id = ?;''', (book_id,)).fetchone()
    if book['checked_out'] == 1:
        checkedOut = 'Yes'

    else:
        checkedOut = 'No'
    if book['restricted'] == 1:
        restricted = 'Yes'

    else:
        restricted = 'No'
    return render_template('book.html', book = book, checkedOut = checkedOut, restricted = restricted)

@app.route('/cart')
@login_required
def cart():
    if 'cart' not in session:
        session['cart'] = {}
        session.modified = True

    titles = {}
    db = get_db()
    for book_id in session['cart']:
        book = db.execute('''SELECT * FROM books
                          WHERE book_id = ?''', (book_id,)).fetchone()
        title = book['title']
        titles[book_id] = title
    return render_template('cart.html', cart= session["cart"])

#might delete quantity???
@app.route('/add_to_cart/<int:book_id>')
@login_required
def add_to_cart(book_id):
    if 'cart' not in session:
        session['cart'] = {}
    if book_id not in session['cart']:
        session['cart'][book_id] = 1

    else: 
        session['cart'][book_id] = session['cart'][book_id] + 1

    session.modified = True
    return redirect(url_for('cart'))

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
            register_date = date.today().strftime('%Y-%m-%d')       #added registration date to database
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
    current_date = date.today().strftime('%y-%m-%d')
    db = get_db()
    books = db.execute('''SELECT * FROM books 
                       WHERE book_id IN (SELECT book_id FROM checkout
               WHERE user_id = ? AND return_date < ? AND is_returned = 1);''',(session['user_id'], current_date)).fetchall()
    return render_template ('books.html', books= books)

@app.route('/checked_out')      
@login_required
def checked_out():
    
    db = get_db()
    books = db.execute('''SELECT * FROM books 
                       WHERE book_id IN (SELECT book_id FROM checkout
               WHERE user_id = ? AND is_returned = 0);''',(session['user_id'], )).fetchall()
    return render_template ('books.html', books= books)

@app.route('/request_book/<int:book_id>', methods = ["GET","POST"])
@login_required
def request_book(book_id):
    today_date = date.today()
    new_return_date = str(today_date + timedelta(days=7))
    
    #can change so that checks also if requested flag already set to yes, if is then does not db.commit
    form = RequestForm()

    message = ''
    if form.validate_on_submit():

        book_id = form.book_id.data 
        db = get_db()
        book = db.execute('''SELECT * FROM books
                WHERE book_id = ?''',(book_id,)).fetchone()
        
        if book['requested'] is not None:
            checkout = db.execute('''SELECT * FROM checkout
                                  WHERE book_id = ? AND is_returned = 0''', (book_id,)).fetchone()
            new_return_date = checkout['return_date']
            message = 'This book has already been requested. It will be available for checkout before: ' + new_return_date
           
        
        elif book['checked_out'] == 1:

            db.execute('''UPDATE books
                       SET requested = 'Yes'
                       WHERE checked_out = 1 AND 
                       book_id = ?;''',(book_id,))
            db.execute('''UPDATE checkout
                       SET return_date = ?
                       WHERE is_returned = 0 AND 
                       book_id = ?;''',(new_return_date, book_id))
            db.commit()
            message = 'This request has been received and processed. The book should be available for checkout before: ' + new_return_date
        
        else:
            message = 'This book is not currently checked out.'
    else:
        if book_id is not None:
            db = get_db()
            book = db.execute('''SELECT * FROM books
                WHERE book_id = ?''', (book_id,)).fetchone()
        
            if book['checked_out'] == 1 and book['requested'] != 'Yes':
                
                db.execute('''UPDATE books
                       SET requested = 'Yes'
                       WHERE checked_out = 1 AND 
                       book_id = ?;''', (book_id,))
                
                
                db.execute('''UPDATE checkout
                       SET return_date = ?
                       WHERE is_returned = 0 AND 
                       book_id = ?;''', (new_return_date, book_id))
                db.commit()
                message = 'This request has been received and processed. The book should be available for checkout before: ' + new_return_date
            else:
                checkout = db.execute('''SELECT * FROM checkout
                                  WHERE book_id = ? AND is_returned = 0''', (book_id,)).fetchone()
                new_return_date = checkout['return_date']
                message = 'This book has already been requested. It will be available for checkout before: ' + new_return_date
        

    return render_template('request_book.html', form = form, message = message, book_id = book_id)

@app.route('/add_book', methods = ["GET","POST"])
def add_book():
    message = ''
    title = ''
    author = ''
    dewey_decimal = ''
    genre = ''
    location = ''
    checked_out = 0
    restricted = 0
    description= ''
    user_id = ''
    if True:       #need is_admin function/ decorator
        form = AddBookForm()
        if form.validate_on_submit():
            
            title = form.title.data
            author = form.author.data
            dewey_decimal = form.dewey_decimal.data
            genre = form.genre.data
            location = form.location.data
            checked_out = form.checked_out.data
            restricted = form.restricted.data
            description= form.description.data 
            user_id = form.user_id.data

            if checked_out == 1 and restricted == 1:
                form.restricted.errors.append('Restricted books cannot be checked out.')
                return render_template('add_book.html', form=form)
            
            else:
                db = get_db()
                db.execute('''INSERT INTO books (title, author, dewey_decimal, genre, location, checked_out, restricted, description)
                            VALUES (?,?,?,?,?,?,?,?);''', (title,author,dewey_decimal,genre,location,checked_out,restricted,description))
                db.commit()
                if checked_out == 1:
                    book = db.execute('''SELECT MAX(book_id) FROM books''').fetchone()
                    

                    today_date = date.today()
                    return_date = str(today_date + timedelta(days=28))
                    db.execute('''INSERT INTO checkout (user_id, book_id, date_checked_out, return_date, extensions, is_returned,is_late)
                            VALUES (?,?,?,?,?,?,?)''',(user_id, book['max(book_id)'], today_date, return_date, 0, 0, 0))
                db.commit()
                #message = 'Book successfully submitted.'
            return redirect(url_for('library'))

    # else:
    #     message = 'You do not have permission to view this page.'

    return render_template('add_book.html', form=form, message=message)

@app.route('/remove_book', methods=["GET","POST"])
def remove_book():
    form = RemoveBookForm()


    if True:        #admin needed
        if form.validate_on_submit():
            book_id = form.book_id.data
            db = get_db()
            db.execute('''DELETE FROM books 
                    WHERE book_id = ?''',(book_id,))
            db.commit()

            return redirect(url_for('library'))


    return render_template('remove_book.html', form=form)

@app.route('/checkout', methods=["GET","POST"])
def checkout(): 
    db = get_db()
    today_date = date.today()
    return_date = str(today_date + timedelta(days=28))
    
    form = CheckoutForm()
    if form.validate_on_submit():
        if 'cart' in session:
            for book_id in session['cart']:
                book = db.execute('''SELECT * FROM books
                        WHERE book_id = ?''',(book_id,)).fetchone()
                if book['checked_out'] == 0:
                    db.execute('''UPDATE books SET checked_out = 1, requested = 0
                        WHERE book_id = ?''',(book_id,))
                    db.execute('''INSERT INTO checkout (user_id, book_id, date_checked_out, return_date, extensions, is_returned,is_late)
                                    VALUES (?,?,?,?,?,?,?)''',(session['user_id'], book_id, today_date, return_date, 0, 0, 0))
                    db.commit()
    if 'cart' not in session or form.validate_on_submit():
        session['cart'] = {}
        session.modified = True
        return redirect(url_for('library'))

    return render_template('checkout.html', form=form, cart = session['cart'])