from flask import Flask, render_template, session, redirect, url_for, g, request
from flask_session import Session
from forms import LoginForm, RegistrationForm, RequestForm, ReturnForm, AddBookForm, RemoveBookForm, CheckoutForm, ChangeIdForm, ChangePasswordForm, LateFeesForm
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date, timedelta, datetime
'''
admin_id = admin, admin_password = password




'''
app = Flask(__name__)
app.config['SECRET_KEY'] = 'LKmfRPwipKUmgzbrYYHYLCdf'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.teardown_appcontext(close_db)

Session(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get('user_id', None)
    g.admin = session.get('admin_id', None)

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.admin is None:
            return redirect(url_for('admin_login', next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

@app.route('/')
def index():

    return render_template('index.html', title='Welcome')

@app.route('/library')
def library():
    db = get_db()
    books = db.execute('''SELECT * FROM books;''').fetchall()

    return render_template('books.html', books=books, title='Library')

@app.route('/library/<int:book_id>')
def book(book_id):
    db = get_db()
    book = db.execute('''SELECT * FROM books
                      WHERE book_id = ?;''', (book_id,)).fetchone()
    user_checkedout = db.execute('''SELECT * FROM checkout 
                               WHERE user_id = ? AND 
                               book_id = ? AND is_returned = 0;''',(session['user_id'],book_id)).fetchone()
    if user_checkedout is None:
        user_checkedout = False
    else:
        user_checkedout = True
    if book['checked_out'] == 1:
        checkedOut = True

    else:
        checkedOut = False
    if book['restricted'] == 1:
        restricted = True

    else:
        restricted = False
    return render_template('book.html', book = book, checkedOut = checkedOut, user_checkedout = user_checkedout,
                           restricted = restricted, title =book['title'])

@app.route('/cart')
@login_required
def cart():
    form = CheckoutForm()
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
    if form.validate_on_submit():
        return redirect(url_for('checkout'))
    return render_template('cart.html', cart= session["cart"], form=form, title='Cart')

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
        
    return render_template('register.html', form=form, title='Registration')
    
@app.route('/login', methods = ["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        password = form.password.data
        if user_id != '' or password !='':
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
                next_page = request.form.get('next')        #request.args.get()   needs fixing in login, admin
                print(next_page)
                if next_page is None:
                    next_page = url_for('index')
                return redirect(next_page)
        else:
            return redirect(url_for('admin_login'))
        
    return render_template('login.html', form=form, title="Login")

@app.route('/admin', methods=["GET","POST"]) 
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        admin_id = form.admin_id.data
        admin_password = form.admin_password.data

        if admin_id == 'admin':
            if admin_password == 'password':
                session.clear()
                session['admin_id'] =  admin_id
                session.modified = True
                next_page = request.args.get('next')
                if not next_page:
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                form.submit2.errors.append('Wrong ID or Password. Did you mean to login as user?')
        else:
            form.submit2.errors.append('Wrong ID or Password. Did you mean to login as user?')
    return render_template('login.html', form=form,title='Login')

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
    return render_template ('books.html', books= books, title='History')

@app.route('/checked_out')      
@login_required
def checked_out():
    
    db = get_db()
    books = db.execute('''SELECT * FROM books 
                       WHERE book_id IN (SELECT book_id FROM checkout
               WHERE user_id = ? AND is_returned = 0);''',(session['user_id'], )).fetchall()
    return render_template ('books.html', books= books,title="Currently Checked Out")

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
                WHERE book_id = ?;''',(book_id,)).fetchone()
        
        if book['requested'] is not None:
            checkout = db.execute('''SELECT * FROM checkout
                                  WHERE book_id = ? AND is_returned = 0;''', (book_id,)).fetchone()
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
                WHERE book_id = ?;''', (book_id,)).fetchone()
        
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
                                  WHERE book_id = ? AND is_returned = 0;''', (book_id,)).fetchone()
                new_return_date = checkout['return_date']
                message = 'This book has already been requested. It will be available for checkout before: ' + new_return_date
        

    return render_template('request_book.html', form = form, message = message, book_id = book_id, title='Request')

@app.route('/add_book', methods = ["GET","POST"])
@admin_required
def add_book():
    
    title = ''
    author = ''
    dewey_decimal = ''
    genre = ''
    location = ''
    checked_out = 0
    restricted = 0
    description= ''
    user_id = ''
    
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
        else:
            db = get_db()
            db.execute('''INSERT INTO books (title, author, dewey_decimal, 
                       genre, location, checked_out, restricted, description)
                        VALUES (?,?,?,?,?,?,?,?);''', (title,author,dewey_decimal,genre,location,checked_out,restricted,description))
            db.commit()
            if checked_out == 1:
                book = db.execute('''SELECT MAX(book_id) FROM books;''').fetchone()
    
                today_date = date.today()
                return_date = str(today_date + timedelta(days=28))
                db.execute('''INSERT INTO checkout (user_id, book_id, date_checked_out, 
                           return_date, extensions, is_returned,is_late)
                        VALUES (?,?,?,?,?,?,?);''',(user_id, book['max(book_id)'], today_date, return_date, 0, 0, 0))
            
            db.commit()
            return redirect(url_for('library'))

    return render_template('add_book.html', form=form, title="Add Book")

@app.route('/remove_book', methods=["GET","POST"])
@admin_required
def remove_book():
    form = RemoveBookForm()    
    if form.validate_on_submit():
        book_id = form.book_id.data
        db = get_db()
        db.execute('''DELETE FROM books 
                WHERE book_id = ?;''',(book_id,))
        db.commit()

        return redirect(url_for('library'))

    return render_template('remove_book.html', form=form, title="Remove Book")

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
                        WHERE book_id = ?;''',(book_id,)).fetchone()
                if book['checked_out'] == 0:
                    db.execute('''UPDATE books SET checked_out = 1, requested = 0
                        WHERE book_id = ?;''',(book_id,))
                    db.execute('''INSERT INTO checkout (user_id, book_id, date_checked_out, return_date, extensions, is_returned,is_late)
                                    VALUES (?,?,?,?,?,?,?);''',(session['user_id'], book_id, today_date, return_date, 0, 0, 0))
                    db.commit()
    if 'cart' not in session or form.validate_on_submit():
        session['cart'] = {}
        session.modified = True
        return redirect(url_for('library'))

    return render_template('cart.html', form=form, cart = session['cart'], title='Cart')

@app.route('/return_books', methods=["GET","POST"])
@login_required
def return_books():
    form = ReturnForm()
    db = get_db()
    today_date = datetime.today()
    
    if form.validate_on_submit():
        book_ids = []
        book_id1 = form.book_id.data
        book_id2 = form.book_id2.data
        
        book_ids.append(book_id1)
        book_ids.append(book_id2)

        for book_id in book_ids:
            if book_id is not None:
                book = db.execute('''SELECT * FROM checkout
                                WHERE book_id = ? AND is_returned = 0;''',(book_id,)).fetchone()
                check = datetime.strptime(book['return_date'], '%Y-%m-%d')

                if check < today_date:
                    db.execute('''UPDATE checkout SET is_late = 1
                           WHERE checkout_id = ?;''',(book['checkout_id'],))
                    db.execute('''UPDATE users SET has_late_fees = 1
                               WHERE user_id =?;''',(session['user_id'],))
                db.execute('''UPDATE books SET checked_out = 0, requested = 0
                            WHERE book_id = ?;''',(book_id,))
                db.execute('''UPDATE checkout SET is_returned = 1
                            WHERE checkout_id = ?;''',(book['checkout_id'],))
                db.commit()

        return redirect(url_for('library'))
    
    return render_template('return_book.html', form=form, title='Return Books')

@app.route('/return_book/<int:book_id>', methods=["GET","POST"])
@login_required
def return_book(book_id):
    today_date = datetime.today()
    db = get_db()

    book = db.execute('''SELECT * FROM checkout
                      WHERE book_id = ? AND is_returned = 0;''',(book_id,)).fetchone()
    if book_id is not None:
        check = datetime.strptime(book['return_date'], '%Y-%m-%d')
        if check < today_date:
             if check < today_date:
                    db.execute('''UPDATE checkout SET is_late = 1
                           WHERE checkout_id = ?;''',(book['checkout_id'],))
                    db.execute('''UPDATE users SET has_late_fees = 1
                               WHERE user_id =?;''',(session['user_id'],))
        db.execute('''UPDATE books SET checked_out = 0, requested = 0
                   WHERE book_id = ?;''',(book_id,))
        db.execute('''UPDATE checkout SET is_returned = 1
                   WHERE checkout_id =?;''',(book['checkout_id'],))    
        db.commit()
        
    return redirect(url_for('return_books'))
    
@app.route('/change_user_id', methods=["GET","POST"])
@admin_required
def change_user_id():
    form = ChangeIdForm()
    db = get_db()

    if form.validate_on_submit():
        past_id = form.past_id.data
        new_id = form.new_id.data

        user = db.execute('''SELECT * FROM users
                          WHERE user_id= ?;''',(past_id,)).fetchone()
        if user is not None:
            db.execute('''UPDATE users SET user_id = ?
                       WHERE user_id = ?;''',(new_id,past_id))
            db.commit()
            return redirect(url_for('login'))

        else: form.past_id.errors.append('This user does not exist.')

    return render_template('change_id.html', form=form, title='Change User ID')

@app.route('/change_password', methods=["GET","POST"])                                                    
def change_password():
    form = ChangePasswordForm()
    db = get_db()
    admin = False
    if 'user_id' in session:
        if form.validate_on_submit():
            old_password = form.old_password.data
            new_password = form.new_password.data
            new_password = generate_password_hash(new_password)

            password = db.execute('''SELECT * FROM users 
                            WHERE user_id =?;''',(session['user_id'],)).fetchone()
            if check_password_hash(password['password'],old_password):
                db.execute('''UPDATE users SET password = ?
                            WHERE user_id = ?''',(new_password, session['user_id']))
                db.commit()
                
                session.clear()
                session.modified = True
                return redirect(url_for('login'))
            else: 
                form.old_password.errors.append('Password is not linked to this account. Please contact an admin.')
        print(form.errors)
    elif 'admin_id' in session:
        admin = True
        if form.validate_on_submit():
            
            user_id = form.user_id.data
            new_password =form.new_password.data
            new_password = generate_password_hash(new_password)
            user = db.execute('''SELECT * FROM users
                            WHERE user_id = ?;''',(user_id,)).fetchone()
            
            if user is not None:
                    print('t')
                    db.execute('''UPDATE users SET password = ?
                                    WHERE user_id =?;''',(new_password,user_id))
                    if user['user_id'] == user_id:    
                        db.commit()
                    else:
                        form.user_id.errors.append('This user does not match any in the database.')
            else:
                form.user_id.errors.append('This user does not match any in the database.')

    else: 
        return redirect(url_for('login'))
    return render_template('change_password.html', form=form, admin = admin, title='Change Password')
            
@app.route('/extend_date/<int:book_id>')
@login_required
def extend_date(book_id):
    today_date = date.today()
    return_date = str(today_date + timedelta(days=28))
    message = ''
    check = True
    db = get_db()
    title = db.execute('''SELECT title FROM books
                       WHERE book_id = ?;''',(book_id,)).fetchone()

    book= db.execute('''SELECT * FROM checkout 
                     WHERE book_id=? AND is_returned = 0;''',(book_id,)).fetchone()
    if book is not None:
        db.execute('''UPDATE checkout SET return_date = ?, extensions = ?
                   WHERE book_id = ? AND is_returned = 0;''',(return_date, book['extensions']+1,book_id))
        if book['extensions'] < 6:
            db.commit()
        else: 
            check = False
            message = '''You have requested an extension 6 times already. This is the max allowed per checkout 
                    instance. Please return the book to the library by: '''
    
    return render_template('extension.html', message = message, check= check, book = book, book_title = title['title'],title='Request Extension')

@app.route('/my_account')
def my_account():
    db = get_db()
    user=False
    admin = False
    if 'admin_id' in session:
        admin =True
    elif 'user_id' not in session:
        return redirect(url_for('login'))
    else:
        user = db.execute('''SELECT * FROM users
                      WHERE user_id =?;''',(session['user_id'],)).fetchone()
    

    return render_template('my_account.html', user=user, title="My Account", admin=admin)

@app.route('/late_fees', methods=["GET","POST"])
@login_required
def late_fees():
    form = LateFeesForm()

    late_fees = 0
    fee = 2
    db = get_db()
    books = db.execute('''SELECT * FROM checkout
                       WHERE user_id = ? AND is_late = 1;''',(session['user_id'],)).fetchall()
    for book in books:
        return_date = datetime.strptime(book['return_date'], '%Y-%m-%d')
        late_date = (datetime.strptime(book['date_checked_out'], '%Y-%m-%d')+ timedelta(days=28))
        difference = return_date - late_date
        difference = difference.days

        late_fees += int(difference) * fee
    user = db.execute('''SELECT * FROM users
                      WHERE user_id =?;''',(session['user_id'],)).fetchone()
    if form.validate_on_submit():
        db.execute('''UPDATE users SET has_late_fees = 0
                   WHERE user_id =?;''',(session['user_id'],))
        db.commit()
        return redirect(url_for('payment'))

    return render_template('my_account.html', late_fees = late_fees, user = user, form=form, title ='My Account')

@app.route('/payment')
@login_required
def payment():

    return render_template('payment.html', title='Thank You!')

#todo: remember me functionality, remote checkout(admin_required)
#need update book.html so that checks if book is checked out by session['user_id], if is add functionality
#need populate database with sensible data (NB return date is 28 days after checkout)