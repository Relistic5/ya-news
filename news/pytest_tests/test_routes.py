from http import HTTPStatus

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pages_availability(client, news):
    """Доступность страниц"""
    urls = (
        ('news:home', None),
        ('news:detail', (news.id,)),
        ('users:login', None),
        ('users:signup', None),
        # ('users:logout', None),  # Что-то с шаблоном
    )
    for name, args in urls:
        response = client.get(reverse(name, args=args))
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(
        client, author, reader, comment):
    """Редактирование и удаление комментариев"""
    client.force_login(author)
    response_edit = client.get(reverse('news:edit', args=(comment.id,)))
    assert response_edit.status_code == HTTPStatus.OK

    client.force_login(reader)
    response_delete = client.get(reverse('news:delete', args=(comment.id,)))
    assert response_delete.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, comment):
    """Редирект"""
    login_url = reverse('users:login')
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url
