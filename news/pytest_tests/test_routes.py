from http import HTTPStatus

import pytest
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
@pytest.mark.parametrize('url_fixture', [
    lf('home_url'),
    lf('detail_url'),
    lf('login_url'),
    lf('signup_url'),
    lf('logout_url'),
])
def test_pages_availability(client, url_fixture):
    """Доступность страниц"""
    response = client.get(url_fixture)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture', ['edit_url', 'delete_url'])
@pytest.mark.django_db
def test_redirect_for_anonymous_client(
        client, request, url_fixture, login_url):
    """Редирект для анонимного пользователя"""
    url = request.getfixturevalue(url_fixture)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url


@pytest.mark.django_db
@pytest.mark.parametrize('user_role, expected_status', [
    ('author', HTTPStatus.OK),
    ('reader', HTTPStatus.NOT_FOUND)
])
def test_edit_and_delete_comment_permissions(
        client, user_role, expected_status, author,
        reader, comment, edit_url, delete_url):
    """Доступ к редактированию и удалению комментариев
    в зависимости от роли пользователя
    """
    if user_role == 'author':
        client.force_login(author)
    elif user_role == 'reader':
        client.force_login(reader)

    response_edit = client.get(edit_url)
    assert response_edit.status_code == expected_status
    response_delete = client.get(delete_url)
    assert response_delete.status_code == expected_status
