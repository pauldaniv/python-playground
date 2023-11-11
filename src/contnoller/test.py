from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# Define a simple model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)

# Database initialization
db.create_all()

# Context manager for transactions
@contextmanager
def transaction(commit=False):
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db.engine))
    try:
        yield session
        if commit:
            session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.remove()

# Transactional decorator
def transactional(func):
    def wrapper(*args, **kwargs):
        with transaction(commit=True) as session:
            return func(*args, session=session, **kwargs)
    return wrapper

# Flask route demonstrating the usage of @transactional
@app.route('/add_book', methods=['POST'])
@transactional
def add_book(session):
    data = request.get_json()
    new_book = Book(title=data['title'])
    session.add(new_book)
    return jsonify(message='Book added successfully.')

# Flask route demonstrating the usage of @transactional
@app.route('/get_books', methods=['GET'])
@transactional
def get_books(session):
    books = Book.query.all()
    book_list = [{'id': book.id, 'title': book.title} for book in books]
    return jsonify(books=book_list)

if __name__ == '__main__':
    app.run(debug=True)
