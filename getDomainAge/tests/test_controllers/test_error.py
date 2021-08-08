from getDomainAge.tests.test_controllers import app, test_client


def test_404_error_page(test_client):
    response = test_client.get('/something_invalid')
    assert response.status_code == 200
    assert 'Congratulation! You have discovered this secret page.' in response.data.decode('utf8')
