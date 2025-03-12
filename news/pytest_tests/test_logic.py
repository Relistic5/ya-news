from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_comment_posting(
        client, detail_url, comment_form):
    """Анонимный пользователь не может комментировать"""
    response = client.post(detail_url, comment_form)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_comment_posting(
        author_client, detail_url, comment_form, news, author):
    """Залогиненный пользователь может комментировать"""
    response = author_client.post(detail_url, comment_form)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1

    created_comment = Comment.objects.last()
    assert created_comment.text == comment_form['text']
    assert created_comment.author == author
    assert created_comment.news == news


@pytest.mark.django_db
def test_author_can_edit_own_comment(
        author_client, comment_form, edit_url, comment):
    """Автор может редактировать собственный комментарий"""
    response = author_client.post(edit_url, data=comment_form)
    assert response.status_code == HTTPStatus.FOUND

    comment.refresh_from_db()
    assert comment.text == comment_form['text']


@pytest.mark.django_db
def test_reader_cannot_edit_another_users_comment(
        reader_client, comment_form, edit_url, comment):
    """Читатель не может редактировать комментарий автора"""
    response = reader_client.post(edit_url, data=comment_form)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment.refresh_from_db()
    assert comment.text == comment.text


@pytest.mark.django_db
def test_author_can_delete_own_comment(
        author_client, comment, delete_url):
    """Автор может удалить свой комментарий"""
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_reader_cannot_delete_another_users_comment(
        reader_client, comment, delete_url):
    """Читатель не может удалить комментарий автора"""
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_bad_comment_posting(author_client, detail_url, bad_word):
    """Комментарий не публикуется при наличии запрещенных слов"""
    bad_comment = f'Этот текст содержит {bad_word}'
    response = author_client.post(detail_url, {'text': bad_comment})
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 0
