from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize("user, expected_status, expected_comment_count", [
    (None, HTTPStatus.FOUND, 0),
    ('author', HTTPStatus.FOUND, 1),
])
def test_user_comment_posting(
        client, detail_url, anonymous_comment, author, user,
        expected_status, expected_comment_count):
    """Доступ к созданию комментариев
    в зависимости от роли пользователя
    """
    if user is not None:
        client.force_login(author)
    response = client.post(detail_url, anonymous_comment)
    assert response.status_code == expected_status
    assert Comment.objects.count() == expected_comment_count
    if user == "author":
        assert Comment.objects.first().text == anonymous_comment['text']
        assert Comment.objects.first().author == author


@pytest.mark.django_db
@pytest.mark.parametrize("user, expected_status", [
    ('author', HTTPStatus.FOUND),
    ('reader', HTTPStatus.NOT_FOUND),
])
def test_user_comment_editing(
        client, edit_url, edit_comment_data, comment,
        author, reader, user, expected_status):
    """Доступ к редактированию комментариев
    в зависимости от роли пользователя
    """
    if user == 'author':
        client.force_login(author)
    elif user == 'reader':
        client.force_login(reader)

    response = client.post(edit_url, edit_comment_data)
    assert response.status_code == expected_status

    if user == 'author':
        comment.refresh_from_db()
        assert comment.text == edit_comment_data['text']
    else:
        comment.refresh_from_db()
        assert comment.text == 'Комментарий Автора'


@pytest.mark.django_db
@pytest.mark.parametrize("user, expected_status", [
    ('author', HTTPStatus.FOUND),
    ('reader', HTTPStatus.NOT_FOUND),
])
def test_user_comment_deleting(
        client, delete_url, comment, author, reader, user, expected_status):
    """Доступ к удалению комментариев
    в зависимости от роли пользователя
    """
    if user == 'author':
        client.force_login(author)
    elif user == 'reader':
        client.force_login(reader)

    response = client.post(delete_url)
    assert response.status_code == expected_status

    if user == 'author':
        assert Comment.objects.count() == 0
    else:
        assert Comment.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    'bad_comment, expected_status, expected_comment_count', [
        (f'Этот текст содержит {word}', HTTPStatus.OK, 0) for word in BAD_WORDS
    ])
def test_bad_comment_posting(
        client, detail_url, bad_comment, expected_status,
        expected_comment_count, author):
    """Комментарий не публикуется при наличии запрещенных слов"""
    client.force_login(author)
    response = client.post(detail_url, {'text': bad_comment})

    assert response.status_code == expected_status
    assert Comment.objects.count() == expected_comment_count
