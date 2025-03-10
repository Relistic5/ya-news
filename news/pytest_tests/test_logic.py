from http import HTTPStatus

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(setup_data, client):
    """Анонимный пользователь не может создать комментарий"""
    news, _ = setup_data
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}

    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(authenticated_client):
    """Зарегистрированный пользователь может создать комментарий"""
    client, news, user = authenticated_client
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}

    response = client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 1

    comment = Comment.objects.get()
    assert comment.text == 'Текст комментария'
    assert comment.news == news
    assert comment.author == user


def test_user_cant_use_bad_words(authenticated_client):
    """Пользователь не может использовать запрещенные слова"""
    client, news, user = authenticated_client
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}

    response = client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'] == [WARNING]

    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client):
    """Автор комментария может его удалить"""
    client, news, author, comment = author_client
    delete_url = reverse('news:delete', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'

    response = client.delete(delete_url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
        reader_client, comment_setup):
    """Читатель не может удалить комментарий другого пользователя"""
    client, _, reader, comment = reader_client
    delete_url = reverse('news:delete', args=(comment.id,))

    response = client.delete(delete_url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client):
    """Автор комментария может его редактировать"""
    client, news, author, comment = author_client
    edit_url = reverse('news:edit', args=(comment.id,))
    new_comment_text = 'Обновлённый комментарий'
    form_data = {'text': new_comment_text}
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'

    response = client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments

    comment.refresh_from_db()
    assert comment.text == new_comment_text


def test_user_cant_edit_comment_of_another_user(reader_client, comment_setup):
    """Читатель не может редактировать комментарий другого пользователя"""
    client, _, reader, comment = reader_client
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновлённый текст'}

    response = client.post(edit_url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
