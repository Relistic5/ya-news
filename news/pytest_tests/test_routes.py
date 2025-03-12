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
@pytest.mark.parametrize(
    'url_fixture', [lf('edit_url'), lf('delete_url')])
@pytest.mark.parametrize('client_fixture, expected_status', [
    (lf('author_client'), HTTPStatus.OK),
    (lf('reader_client'), HTTPStatus.NOT_FOUND)
])
def test_comment_permissions(
        request, client_fixture, expected_status, url_fixture):
    """Доступ к редактированию и удалению комментариев
    в зависимости от роли пользователя.
    """
    client = client_fixture
    url = url_fixture
    response = client.get(url)
    assert response.status_code == expected_status
