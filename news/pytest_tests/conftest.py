import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from news.models import News, Comment


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
    """Вход в уч.запись"""
    return reverse_lazy('users:login')

@pytest.fixture
def login_out():
    """Выход из уч.записи"""
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
def author(db):
    """Создаем автора"""
    return User.objects.create(username='Автор')


@pytest.fixture
def reader(db):
    """Создаем читателя"""
    return User.objects.create(username='Читатель')


@pytest.fixture
def news(db):
    """Создаем новость"""
    return News.objects.create(
        title="Заголовок", text="Текст новости")


@pytest.fixture
def comment(author, news):
    """Создаем комментарий Автора"""
    return Comment.objects.create(
        text='Комментарий Автора', author=author, news=news)
