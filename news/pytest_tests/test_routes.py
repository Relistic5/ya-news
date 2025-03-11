from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazy_fixtures import lf


@pytest.mark.django_db
@pytest.mark.parametrize('url_fixture', (
    lf('home_url'),
    lf('detail_url'),
    lf('login_url'),
    lf('signup_url'),
    lf('logout_url'),
))
def test_pages_availability(client, url_fixture):
    """Доступность страниц"""
    response = client.get(url_fixture)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url_fixture', ('edit_url', 'delete_url'))
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, request,
                                       url_fixture, login_url):
    """Редирект для анонимного пользователя"""
    url = request.getfixturevalue(url_fixture)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == redirect_url
    assertRedirects(response, redirect_url)


@pytest.mark.django_db
@pytest.mark.parametrize('user_role, expected_status', [
    ('author', HTTPStatus.OK),
    ('reader', HTTPStatus.NOT_FOUND)
])
@pytest.mark.parametrize('action', ('edit', 'delete'))
def test_comment_permissions(client, user_role, expected_status, author,
                             reader, comment, edit_url, delete_url, action):
    """Доступ к редактированию и удалению комментариев
    в зависимости от роли пользователя
    """
    if user_role == 'author':
        client.force_login(author)
    elif user_role == 'reader':
        client.force_login(reader)

    url = edit_url if action == 'edit' else delete_url
    response = client.get(url)
    assert response.status_code == expected_status
