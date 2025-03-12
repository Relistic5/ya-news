import pytest
from pytest_lazy_fixtures import lf

from news.forms import CommentForm
from yanews import settings


@pytest.mark.django_db
def test_home_page_news_count(author_client, create_news, home_url):
    """Количество новостей на Главной"""
    response = author_client.get(home_url)
    assert 'object_list' in response.context, 'Ключ отсутствует'
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_page_news_sorted(author_client, create_news, home_url):
    """Сортировка новостей - от старых к новым"""
    response = author_client.get(home_url)
    assert 'object_list' in response.context, 'Ключ отсутствует'
    object_list = response.context['object_list']
    pub_dates = [news.date for news in object_list]
    assert pub_dates == sorted(pub_dates, reverse=True)


@pytest.mark.django_db
def test_news_comments_sorted(reader_client, create_news_and_comments,
                              comment, detail_url):
    """Сортировка комментариев - от старых к новым"""
    response = reader_client.get(detail_url)
    comments = response.context['object'].comment_set.all().order_by('created')
    creation_dates = [comment.created for comment in comments]
    assert creation_dates == sorted(creation_dates)


@pytest.mark.django_db
@pytest.mark.parametrize('client_fixture, expected_form', [
    (lf('client'), False),
    (lf('author_client'), True)
])
def test_comment_form_access(
        request, news, detail_url, client_fixture, expected_form):
    """Наличие формы комментариев на странице новости
    в зависимости от роли пользователя
    """
    client = client_fixture
    response = client.get(detail_url)
    assert ('form' in response.context) == expected_form
    if expected_form:
        assert isinstance(response.context['form'], CommentForm)
