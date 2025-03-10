import pytest
from django.contrib.auth import get_user_model

from news.models import News, Comment


User = get_user_model()


@pytest.fixture
def news():
    """Создаем новость"""
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def author():
    """Создаем автора для комментариев"""
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def reader():
    """Создаем читателя для комментариев"""
    return User.objects.create(username='Читатель простой')


@pytest.fixture
def comment(news, author):
    """Создаем комментарий"""
    return Comment.objects.create(
        news=news, author=author, text='Текст комментария')


@pytest.fixture
def logged_in_client(client, author):
    """Создаем авторизованного клиента"""
    client.force_login(author)
    return client


@pytest.fixture
def setup_data(db):
    """Создаем новость и пользователя"""
    news = News.objects.create(title='Заголовок', text='Текст')
    user = User.objects.create(username='Мимо Крокодил')
    return news, user


@pytest.fixture
def authenticated_client(setup_data, client):
    """Создаем авторизованного клиента с доступом к новости"""
    news, user = setup_data
    client.force_login(user)
    return client, news, user


@pytest.fixture
def comment_setup(db):
    """Создаем данные для тестирования комментариев"""
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Автор комментария')
    reader = User.objects.create(username='Читатель')

    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )

    return news, author, reader, comment


@pytest.fixture
def author_client(comment_setup, client):
    """Создаем авторизованного клиента - автора комментария"""
    news, author, _, comment = comment_setup
    client.force_login(author)
    return client, news, author, comment


@pytest.fixture
def reader_client(comment_setup, client):
    """Создаем авторизованного клиента - читателя"""
    news, _, reader, comment = comment_setup
    client.force_login(reader)
    return client, news, reader, comment
