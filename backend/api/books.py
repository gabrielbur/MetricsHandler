from flask import Blueprint, jsonify, request
from flask_login import login_required
from loguru import logger
from marshmallow import Schema, fields, ValidationError

# Create a schema to validate book data
class BookSchema(Schema):
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    isbn = fields.Str(required=True)


def init_books_module(app, mongo, login_manager):
    books_bp = Blueprint('books', __name__)
    
    @books_bp.route('/', methods=['GET', 'POST','OPTIONS'])
    #@login_required
    def get_books():
        try:
            books_collection = mongo.db.books
            books_data = list(books_collection.find())

            # Convert ObjectId to string for each book
            for book in books_data:
                book['_id'] = str(book['_id'])

            return jsonify({'books': books_data}), 200
        except Exception as e:
            logger.error(f"Error in /books route: {e}")
            return jsonify({'message': 'Internal Server Error'}), 500

    @books_bp.route('/add', methods=['POST'])
    @login_required
    def add_book():
        try:
            # Validate incoming JSON data
            book_data = request.get_json()
            logger.debug(f"Received request: {book_data}")
            schema = BookSchema()
            errors = schema.validate(book_data)
            if errors:
                return jsonify({'message': 'Invalid input data', 'errors': errors}), 400

            # Insert the validated book data into the database
            books_collection = mongo.db.books
            result = books_collection.insert_one(book_data)

            if result.inserted_id:
                return jsonify({'message': 'Book added successfully', 'book_id': str(result.inserted_id)}), 201
            else:
                return jsonify({'message': 'Failed to add book'}), 500
        except ValidationError as e:
            return jsonify({'message': 'Invalid input data', 'errors': e.messages}), 400
        except Exception as e:
            logger.error(f"Error in /books/add route: {e}")
            return jsonify({'message': 'Internal Server Error'}), 500

    app.register_blueprint(books_bp, url_prefix='/books')
