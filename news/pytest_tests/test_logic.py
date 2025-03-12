import random
import string
from http import HTTPStatus

import pytest

from news.forms import BAD_WORDS
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_comment_posting(
        client, detail_url, comment):
    """Анонимный пользователь не может комментировать"""
    response = client.post(detail_url, {'text': comment.text})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_comment_posting(
        author_client, detail_url, comment):
    """Залогиненный пользователь может комментировать"""
    response = author_client.post(detail_url, {'text': comment.text})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 2
    created_comment = Comment.objects.last()
    assert created_comment.text == comment.text
    assert created_comment.author == comment.author
    assert created_comment.news == comment.news


@pytest.mark.django_db
def test_author_can_edit_own_comment(
        author_client, comment, edit_url):
    """Автор может редактировать собственный комментарий"""
    new_text = ''.join(random.choices(
        string.ascii_letters + string.digits, k=10))
    form_data = {'text': new_text}
    response = author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND

    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == form_data['text']


@pytest.mark.django_db
def test_reader_cannot_edit_another_users_comment(
        reader_client, comment, edit_url):
    """Читатель не может редактировать комментарий автора"""
    original_text = comment.text
    new_text = ''.join(random.choices(
        string.ascii_letters + string.digits, k=10))
    form_data = {'text': new_text}
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == original_text


@pytest.mark.django_db
def test_author_can_delete_own_comment(
        author_client, comment, delete_url):
    """Автор может удалить свой комментарий"""
    response = author_client.post(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_reader_cannot_delete_another_users_comment(
        reader_client, comment, delete_url):
    """Читатель не может удалить комментарий автора"""
    response = reader_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_bad_comment_posting(
        author_client, detail_url, bad_word,
        expected_status=HTTPStatus.OK, expected_comment_count=0):
    """Комментарий не публикуется при наличии запрещенных слов"""
    bad_comment = f'Этот текст содержит {bad_word}'
    response = author_client.post(detail_url, {'text': bad_comment})

    assert response.status_code == expected_status
    assert Comment.objects.count() == expected_comment_count
