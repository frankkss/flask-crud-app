import os
import tempfile
import pytest
from bookmanager import app, db, Book

@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    os.close(db_fd)
    os.unlink(db_path)

def test_home_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Add Book' in rv.data

def test_add_book(client):
    rv = client.post('/', data={'title': 'Test Book'})
    assert rv.status_code == 200
    assert b'Book added successfully' in rv.data

def test_add_duplicate_book(client):
    client.post('/', data={'title': 'Test Book'})
    rv = client.post('/', data={'title': 'Test Book'})
    assert rv.status_code == 200
    assert b'Book with this title already exists' in rv.data

def test_update_book(client):
    client.post('/', data={'title': 'Old Title'})
    rv = client.post('/update', data={'oldtitle': 'Old Title', 'newtitle': 'New Title'})
    assert rv.status_code == 302  # Redirect to home
    rv = client.get('/')
    assert b'New Title' in rv.data

def test_delete_book(client):
    client.post('/', data={'title': 'Test Book'})
    rv = client.post('/delete', data={'title': 'Test Book'})
    assert rv.status_code == 302  # Redirect to home
    rv = client.get('/')
    assert b'Test Book' not in rv.data
