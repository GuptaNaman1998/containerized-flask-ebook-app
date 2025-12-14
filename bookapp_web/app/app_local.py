# abcd@gmail.com
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email
from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import csv
import os
from sqlalchemy.sql import text  # Import text from sqlalchemy.sql

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "super secret key"

# Configure database
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
database_path = os.path.join(basedir, 'var', 'app-instance', 'books.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{database_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'sql', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Enable debug mode
app.debug = True

# Initialize database
db = SQLAlchemy(app)

class book_1():
    id = 1
    title = 'Moby Dick; Or, The Whale'
    author = 'Herman Melville'
    description = 'A tale of the whale hunt and revenge.'
    pdf_loc = '/static/pdfs/Moby Dick; Or, The Whale.pdf'
    cover_img_loc = '/static/images/Moby Dick; Or, The Whale.png'
    published_on = '1851-10-18'
    genre = 'Fiction'

class book_2():
    id = 2
    title = 'Pride and Prejudice'
    author = 'Jane Austen'
    description = 'A classic romance novel.'
    pdf_loc = '/static/pdfs/Pride and Prejudice.pdf'
    cover_img_loc = '/static/images/Pride and Prejudice.png'
    published_on = '1813-01-28'
    genre = 'Romance'

class book_3():
    id = 3
    title = 'Romeo and Juliet'
    author = 'William Shakespeare'
    description = 'A timeless tragedy of star-crossed lovers.'
    pdf_loc = '/static/pdfs/Romeo and Juliet.pdf'
    cover_img_loc = '/static/images/Romeo and Juliet.png'
    published_on = '1597-01-01'
    genre = 'Drama'

# Data Models
class User(db.Model, UserMixin):
    """
    Model for user accounts.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

class Book(db.Model):
    """
    Model for books.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    translator = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    pdf_loc = db.Column(db.String(100))
    cover_img_loc = db.Column(db.String(100))
    published_on = db.Column(db.Date)
    genre = db.Column(db.String(100))

    def __repr__(self):
        return f'<Book {self.id}>'

class ReadingProgress(db.Model):
    """
    Model to store reading progress for each user and book.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    last_read_page = db.Column(db.Integer, nullable=True)
    progress_percentage = db.Column(db.Float, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Forms
class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username = StringField('Username/Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class SignupForm(FlaskForm):
    """
    Form for user signup.
    """
    username = StringField('Username/Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID for Flask-Login.
    """
    app.logger.debug(f"Loading user with ID: {user_id}")
    return User.query.get(int(user_id))

# Utility Functions
def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    """
    app.logger.debug(f"Checking if file '{filename}' is allowed.")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/signup', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])  # Add '/' route
def signup():
    """
    Route for the signup page.
    """
    app.logger.debug("Rendering signup page.")
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = username if '@' in username else None
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('login'))
        else:
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for the login page.
    """
    app.logger.debug("Rendering login page.")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('library'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template('login.html', form=form)

@app.route('/library')
# @login_required
def bookshelf():
    """
    Route for the library page.
    Fetches all books from the database, including the books read by the current user.
    """
    # app.logger.debug(f"Fetching library for user ID: {current_user.id}")
    try:
        # books = Book.query.all()
        # user_progress = ReadingProgress.query.filter_by(user_id=current_user.id).all()
        # read_books = {progress.book_id: progress.last_read_page for progress in user_progress}
        # read_books = {progress.book_id: progress.last_read_page for progress in user_progress}
        books = {book_1(), book_2(), book_3()}

        # app.logger.debug(f"Fetched {len(books)} books from the database.")
        # app.logger.debug(f"Fetched progress for user {current_user.id}: {read_books}")

        return render_template('bookshelf.html', books=books)#, read_books=read_books)
    except Exception as e:
        app.logger.error(f"Error fetching books or user progress: {e}")
        flash('Error fetching books. Please try again later.', 'danger')
        return "nothing to show"
    
@app.route('/book_details/<int:book_id>')
# @login_required
def book_detail(book_id):
    """
    Route to display the details of a specific book, including its embedded PDF.
    Fetches book details from the database using the book ID.
    """
    app.logger.debug(f"Fetching details for book ID: {book_id}")
    try:
        # Create a mapping of book IDs to book classes
        book_classes = {
            1: book_1,
            2: book_2,
            3: book_3
        }
        
        if book_id not in book_classes:
            book = None
        else:
            book = book_classes[book_id]()
            
        if not book:
            app.logger.warning(f"Book with ID {book_id} not found.")
            flash('Book not found.', 'danger')
            return redirect(url_for('bookshelf'))
        app.logger.debug(f"Fetched details for book ID {book_id}: {book}")
        return render_template('book_details.html', book=book)
    except Exception as e:
        app.logger.error(f"Error fetching book details for ID {book_id}: {e}")
        flash('Error fetching book details. Please try again later.', 'danger')
        return redirect(url_for('bookshelf'))

@app.route('/books/<int:book_id>')
# @login_required
def read_book(book_id):
    """
    Route to display the details of a specific book, including its embedded PDF.
    Fetches book details from the database using the book ID.
    Checks reading progress and continues from the last read page if available.
    """
    app.logger.debug(f"Fetching book for reading with ID: {book_id}")
    try:
        # Create a mapping of book IDs to book classes
        book_classes = {
            1: book_1,
            2: book_2,
            3: book_3
        }
        
        if book_id not in book_classes:
            book = None
        else:
            book = book_classes[book_id]()
        if not book:
            app.logger.warning(f"Book with ID {book_id} not found.")
            flash('Book not found.', 'danger')
            return redirect(url_for('bookshelf'))

        # Check reading progress
        # progress = ReadingProgress.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        last_read_page = 1

        app.logger.debug(f"Fetched details for book ID {book_id}: {book}")
        # app.logger.debug(f"Last read page for user {current_user.id} and book {book_id}: {last_read_page}")

        return render_template('book.html', book=book, last_read_page=last_read_page)
    except Exception as e:
        app.logger.error(f"Error fetching book details for ID {book_id}: {e}")
        flash('Error fetching book details. Please try again later.', 'danger')
        return redirect(url_for('bookshelf'))

@app.route('/profile')
# @login_required
def profile():
    """
    Route for the user profile page.
    Displays the current user's profile information.
    """
    app.logger.debug(f"Fetching profile for user ID: {current_user.id}")
    try:
        user = current_user
        app.logger.debug(f"Fetched profile for user ID {user.id}: {user}")
        return render_template('profile.html', user=user)
    except Exception as e:
        app.logger.error(f"Error fetching user profile: {e}")
        flash('Error fetching profile. Please try again later.', 'danger')
        return redirect(url_for('login'))

@app.route('/settings')
@login_required
def settings():
    """
    Route for the settings page.
    """
    app.logger.debug(f"Rendering settings page for user ID: {current_user.id}")
    return render_template('settings.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    """
    Route for logging out the user.
    """
    app.logger.debug(f"Logging out user ID: {current_user.id}")
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    """
    Route for the admin page.
    """
    app.logger.debug(f"Rendering admin page for user ID: {current_user.id}")
    if not current_user.is_admin:
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('bookshelf'))
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/upload_books_data', methods=['POST'])
@login_required
def upload_books_data():
    """
    Route to handle uploading SQL or CSV files for books data.
    """
    app.logger.debug(f"Processing file upload for user ID: {current_user.id}")
    if not current_user.is_admin:
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('admin'))

    app.logger.debug(f"Request data: {request.files}")

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin'))

    file = request.files['file']
    app.logger.debug(f"Uploaded file name: {file.filename}")

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()

        if file_ext == 'csv':
            try:
                # Read and process CSV file
                csv_data = csv.DictReader(file.stream.read().decode('utf-8').splitlines())
                for row in csv_data:
                    app.logger.debug(f"CSV Row: {row}")
                    new_book = Book(
                        title=row['title'],
                        author=row['author'],
                        description=row.get('description', ''),
                        pdf_loc=row.get('pdf_loc', ''),
                        cover_img_loc=row.get('cover_img_loc', ''),
                        published_on=datetime.strptime(row['published_on'], '%Y-%m-%d').date() if row.get('published_on') else None,
                        genre=row.get('genre', '')
                    )
                    db.session.add(new_book)
                db.session.commit()
                flash('Books data uploaded successfully!', 'success')
            except Exception as e:
                app.logger.error(f"Error processing CSV file: {e}")
                flash(f'Error processing CSV file: {e}', 'danger')

        elif file_ext == 'sql':
            try:
                # Read and execute SQL script
                sql_script = file.stream.read().decode('utf-8')
                app.logger.debug(f"SQL Script Content: {sql_script}")
                db.session.execute(text(sql_script))
                db.session.commit()
                flash('SQL script executed successfully!', 'success')
            except Exception as e:
                app.logger.error(f"Error executing SQL script: {e}")
                flash(f'Error executing SQL script: {e}', 'danger')

    else:
        flash('Invalid file type. Only .sql and .csv files are allowed.', 'danger')

    return redirect(url_for('admin'))

@app.route('/docs')
def docs():
    """
    Route for serving the documentation.
    """
    app.logger.debug("Rendering documentation page.")
    return render_template('docs.html')

@app.route('/api/progress', methods=['POST'])
@login_required
def save_progress():
    """
    API endpoint to save reading progress.
    Checks if an entry exists for the user and book. If found, updates the entry; otherwise, creates a new one.
    """
    app.logger.debug(f"Saving progress for user ID: {current_user.id}")
    try:
        data = request.json
        book_id = data.get('book_id')
        current_page = data.get('last_read_page')
        progress_percentage = data.get('progress_percentage')

        if not book_id or current_page is None or progress_percentage is None:
            app.logger.warning("Incomplete data received for saving progress.")
            return {'message': 'Incomplete data'}, 400

        # Check if progress already exists
        progress = ReadingProgress.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if progress:
            app.logger.debug(f"Updating progress for user {current_user.id} and book {book_id}.")
            progress.last_read_page = current_page
            progress.progress_percentage = progress_percentage
            progress.updated_at = datetime.now(timezone.utc)
        else:
            app.logger.debug(f"Creating new progress entry for user {current_user.id} and book {book_id}.")
            progress = ReadingProgress(
                user_id=current_user.id,
                book_id=book_id,
                last_read_page=current_page,
                progress_percentage=progress_percentage,
                updated_at=datetime.now(timezone.utc)
            )
            db.session.add(progress)

        db.session.commit()
        app.logger.info(f"Progress saved successfully for user {current_user.id} and book {book_id}.")
        return {'message': 'Progress saved successfully'}, 200
    except Exception as e:
        app.logger.error(f"Error saving progress: {e}")
        return {'message': 'Error saving progress'}, 500

@app.route('/api/progress/<int:book_id>', methods=['GET'])
@login_required
def get_progress(book_id):
    """
    API endpoint to retrieve reading progress for a specific book.
    """
    app.logger.debug(f"Fetching progress for book ID: {book_id} and user ID: {current_user.id}")
    progress = ReadingProgress.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if progress:
        return {
            'last_read_page': progress.last_read_page,
            'progress_percentage': progress.progress_percentage
        }, 200
    return {'message': 'No progress found for this book'}, 404

@app.route('/current_user')
@login_required
def current_user_info():
    """
    Route to display the current logged-in user's information.
    """
    app.logger.debug(f"Fetching current user info for user ID: {current_user.id}")
    user_info = {
        'username': current_user.username,
        'email': current_user.email,
        'is_admin': current_user.is_admin
    }
    return render_template('current_user.html', user_info=user_info)

if __name__ == "__main__":
    try:
        with app.app_context():
            db.create_all()
            app.logger.info("Database tables created successfully.")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {e}")
    app.run(debug=True, host='0.0.0.0', port=5000)
    app.logger.info("Flask app is running.")