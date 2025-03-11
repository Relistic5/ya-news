import pytest

from yanews import settings


@pytest.mark.django_db
def test_home_page_news_count(client, create_news, home_url):
    """Количество новостей на Главной"""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_page_news_sorted(client, create_news, home_url):
    """Сортировка новостей - от старых к новым"""
    response = client.get(home_url)
    object_list = response.context['object_list']
    pub_dates = [news.date for news in object_list]
    assert pub_dates == sorted(pub_dates, reverse=True)


@pytest.mark.django_db
def test_news_comments_sorted(client, create_news_and_comments, comment, detail_url):
    """Сортировка комментариев - от старых к новым"""
    response = client.get(detail_url)
    comments = response.context['object'].comment_set.all().order_by('created')
    creation_dates = [comment.created for comment in comments]
    assert creation_dates == sorted(creation_dates)


@pytest.mark.django_db
@pytest.mark.parametrize('user_role, expected_form', [
    (None, False),
    ('author', True)
])
def test_comment_form_access(
        client, news, detail_url, author, user_role, expected_form):
    """Наличие формы комментариев на странице новости
    в зависимости от роли пользователя
    """
    if user_role == 'author':
        client.force_login(author)
    response = client.get(detail_url)
    assert ('form' in response.context) == expected_form
