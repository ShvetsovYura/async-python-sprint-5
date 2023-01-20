from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from core.config import BASE_DIR

from .mocks import CustomTestUser

new_test_user = CustomTestUser()
default_user = CustomTestUser('test_user')


async def test_register_user(client: AsyncClient) -> None:
    response = await client.post(
        app.url_path_for('signup'),
        json={
            'name': new_test_user.name,
            'password': new_test_user.password,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert 'name' in response.json()
    assert response.json().get('name') == new_test_user.name
    assert 'id' in response.json()


async def test_get_token(client: AsyncClient) -> None:
    response = await client.post(
        app.url_path_for('signin'),
        data={
            'username': default_user.name,
            'password': default_user.password,
        },
    )
    assert response.status_code == status.HTTP_202_ACCEPTED

    assert 'access_token' in response.json()
    assert 'expires' in response.json()
    assert 'token_type' in response.json()
    assert response.json().get('token_type') == 'bearer'


async def test_get_user_info(client: AsyncClient) -> None:
    auth_response = await client.post(
        app.url_path_for('signin'),
        data={
            'username': default_user.name,
            'password': default_user.password,
        },
    )
    token_: str = auth_response.json().get('access_token')
    response = await client.get(app.url_path_for('who_i_am'),
                                headers={'Authorization': f'Bearer {token_}'})

    assert response.status_code == status.HTTP_200_OK
    assert 'name' in response.json()
    assert response.json().get('name') == default_user.name
    assert 'id' in response.json()
    assert response.json().get('id') > 0


async def test_get_availability_services(client: AsyncClient) -> None:
    response = await client.get(app.url_path_for('get_ping'))
    assert response.status_code == status.HTTP_200_OK
    assert 'datebase' in response.json()
    assert 'redis' in response.json()


async def test_upload_file(client: AsyncClient) -> None:
    auth_response = await client.post(
        app.url_path_for('signin'),
        data={
            'username': default_user.name,
            'password': default_user.password,
        },
    )
    token_: str = auth_response.json().get('access_token')

    response = await client.post(
        app.url_path_for('upload_file'),
        params={'path': 'test_dir'},
        files={
            'file': ('test_file.txt', open(BASE_DIR + '/tests/resources/sample_file.txt', 'rb')),
        },
        headers={'Authorization': f'Bearer {token_}'},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert 'status' in response.json()
    assert response.json().get('status') == ('Successfully uploaded test_file.txt')
    assert 'size' in response.json()


async def test_get_file_list(client: AsyncClient, async_session: AsyncSession) -> None:
    auth_response = await client.post(
        app.url_path_for('signin'),
        data={
            'username': default_user.name,
            'password': default_user.password,
        },
    )
    token_: str = auth_response.json().get('access_token')

    await client.post(
        app.url_path_for('upload_file'),
        params={'path': 'test_dir'},
        files={
            'file': ('test_file.txt', open(BASE_DIR + '/tests/resources/sample_file.txt', 'rb')),
        },
        headers={'Authorization': f'Bearer {token_}'},
    )

    response = await client.get(app.url_path_for('get_files_list'),
                                headers={'Authorization': f'Bearer {token_}'})
    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response.json()
    assert isinstance(response.json().get('items'), list)
    assert len(response.json().get('items')) == 1
    assert 'total' in response.json()
    assert response.json().get('total') == 1
