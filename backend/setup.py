from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from faker import Faker
import datetime
from datetime import timezone, timedelta
import random

fake = Faker()

# MongoDB URI
mongo_uri = 'mongodb://localhost:27017/booksdb'
client = MongoClient(mongo_uri)
db = client.booksdb

# Create a local Bcrypt instance
bcrypt = Bcrypt()

def random_timestamps(start, end, n=1000):
    """Generate n random timestamps between start and end dates."""
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_timestamps = [start + timedelta(seconds=random.randint(0, int_delta)) for _ in range(n)]
    return random_timestamps

def setup():
    users = db.users
    books = db.books
    metrics = db.metrics

    # Check if the user already exists
    existing_user = users.find_one({'username': 'example'})
    if existing_user:
        print('User already exists. Skipping user setup.')
    else:
        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')

        # Insert the user into the 'users' table with hashed password and timestamp
        user_data = {
            '_id': 1,
            'username': 'example',
            'password': hashed_password,
            'created': datetime.datetime.now(timezone.utc),
            'lastUpdated': datetime.datetime.now(timezone.utc),
        }
        users.insert_one(user_data)
        print('User setup complete.')

    # Check if books already exist
    existing_books_count = books.count_documents({})
    if existing_books_count >= 10:
        print('Books already exist. Skipping books setup.')
    else:
        # Insert 10 books into the 'books' table with timestamp
        for _ in range(10):
            book_data = {
                'title': fake.sentence(nb_words=3),
                'author': fake.name(),
                'isbn': fake.isbn10(),
                'created': datetime.datetime.now(timezone.utc),
                'lastUpdated': datetime.datetime.now(timezone.utc),
            }
            books.insert_one(book_data)

        print('Books setup complete.')

    # Check if metrics already exist
    existing_metrics_count = metrics.count_documents({})
    if existing_metrics_count > 0:
        print('Metrics already exist. Skipping metrics setup.')
    else:
        now = datetime.datetime.now(timezone.utc)
        five_days_ago = now - timedelta(days=5)
        timestamps = random_timestamps(five_days_ago, now)

        for timestamp in timestamps:
            metric_data = {
                'name': 'metric_example',
                'value': fake.random_number(digits=3),  # or use random.randint for a range
                'timestamp': timestamp,
            }
            metrics.insert_one(metric_data)

        # Create indexes
        metrics.create_index([('name', 1)])
        metrics.create_index([('value', 1)])
        metrics.create_index([('timestamp', 1)])

        print('Metrics setup complete.')

if __name__ == '__main__':
    setup()
