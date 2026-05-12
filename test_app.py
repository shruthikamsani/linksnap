import pytest
import os
from app import app, init_db

TEST_DB = 'test_linksnap.db'

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    monkeypatch.setattr('app.DATABASE', TEST_DB)
    init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'linksnap'

def test_homepage_loads(client):
    response = client.get('/')
    assert response.status_code == 200

def test_shorten_url(client):
    response = client.post('/shorten',
                           json={'url': 'https://www.google.com'},
                           content_type='application/json')
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_url' in data
    assert 'code' in data
    assert len(data['code']) == 6

def test_redirect_works(client):
    response = client.post('/shorten',
                           json={'url': 'https://www.python.org'},
                           content_type='application/json')
    code = response.get_json()['code']
    redirect_response = client.get(f'/{code}')
    assert redirect_response.status_code == 302
    assert 'python.org' in redirect_response.location

def test_unknown_code_returns_404(client):
    response = client.get('/doesnotexist')
    assert response.status_code == 404

def test_shorten_missing_url(client):
    response = client.post('/shorten',
                           json={},
                           content_type='application/json')
    assert response.status_code == 400

def test_stats_endpoint(client):
    response = client.post('/shorten',
                           json={'url': 'https://www.github.com'},
                           content_type='application/json')
    code = response.get_json()['code']
    stats = client.get(f'/api/stats/{code}')
    assert stats.status_code == 200
    data = stats.get_json()
    assert data['short'] == code
    assert data['clicks'] == 0

def test_click_count_increases(client):
    response = client.post('/shorten',
                           json={'url': 'https://www.example.com'},
                           content_type='application/json')
    code = response.get_json()['code']
    client.get(f'/{code}')
    client.get(f'/{code}')
    stats = client.get(f'/api/stats/{code}')
    assert stats.get_json()['clicks'] == 2