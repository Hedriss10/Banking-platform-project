import pytest
from unittest.mock import patch
from flask import url_for
from src.models.bsmodels import User

@patch('src.models.bsmodels.User.query')
def test_get_user(mock_query, client, app):
    mock_users = [
        User(username='testuser1', lastname='testlast1', email='test1@example.com', user_identification='123', password='12345', typecontract='Funcionario', type_user_func='admin'),
        User(username='testuser2', lastname='testlast2', email='test2@example.com', user_identification='456', password='12345', typecontract='Funcionario', type_user_func='user')
    ]
    
    mock_query.filter.return_value.order_by.return_value.paginate.return_value.items = mock_users

    with client.session_transaction() as session:
        session['_user_id'] = '1'
        session['_fresh'] = True 

    with app.test_request_context():
        response = client.get(
            url_for('users.users', page=1),
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

    assert response.status_code == 200