from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils import timezone

from news.models import News, Comment
from yanews import settings

User = get_user_model()


@pytest.fixture
def home_url():
    """Главная страница"""
    return reverse_lazy('news:home')


@pytest.fixture
def detail_url(news):
    """Страница новости"""
    return reverse_lazy('news:detail', args=(news.id,))


@pytest.fixture
def login_url():
    """Страница входа в уч.запись"""
    return reverse_lazy('users:login')


@pytest.fixture
def login_out():
    """Страница выхода из уч.записи"""
    return reverse_lazy('users:logout')


@pytest.fixture
def signup_url():
    """Страница регистрации"""
    return reverse_lazy('users:signup')


@pytest.fixture
def edit_url(comment):
    """Страница редактирования комментария"""
    return reverse_lazy('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    """Страница удаления комментария"""
    return reverse_lazy('news:delete', args=(comment.id,))


@pytest.fixture
def author():
    """Создаем автора"""
    return User.objects.create(username='Автор')


@pytest.fixture
def reader():
    """Создаем читателя"""
    return User.objects.create(username='Читатель')


@pytest.fixture
def news():
    """Создаем новость"""
    return News.objects.create(
        title="Новость", text="Текст новости")


@pytest.fixture
def anonymous_comment(news):
    """Создаем комментарий"""
    return {'text': 'Какой-то комментарий'}


@pytest.fixture
def comment(author, news):
    """Создаем комментарий Автора"""
    return Comment.objects.create(
        text='Комментарий Автора', author=author, news=news)


@pytest.fixture
def edit_comment_data():
    """Редактируем комментарий Автора"""
    return {'text': 'Обновлённый комментарий Автора'}


@pytest.fixture
def create_news():
    """Создаем несколько новостей с разными датами"""
    now = timezone.now()
    news_list = [
        News(title=f'Новость {index}',
             text='Текст новости.',
             date=now - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def create_news_and_comments(author, news):
    """Создаем новость и комментарии к ней"""
    now = timezone.now()
    news_item = news
    comment_list = [
        Comment(news=news_item,
                author=author,
                text=f'Комментарий {index}',
                created=now - timedelta(minutes=index))
        for index in range(5)
    ]
    Comment.objects.bulk_create(comment_list)
    return news_item
