from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone

from news.forms import CommentForm
from news.models import News, Comment


@pytest.mark.django_db
def test_home_page_news_count(client):
    """Тест главной страницы на количество новостей"""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    response = client.get(reverse_lazy('news:home'))
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_page_news_order(client):
    """Тест главной страницы на сортировку новостей"""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    response = client.get(reverse_lazy('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page_comments_order(news, author, client):
    """Тест страницы новости на сортировку комментариев"""
    detail_url = reverse_lazy('news:detail', args=(news.id,))
    now = timezone.now()

    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()

    response = client.get(detail_url)
    assert 'news' in response.context
    news_instance = response.context['news']
    all_comments = news_instance.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(news, client):
    """Для анонимного клиента - форма комментария НЕ отображается"""
    detail_url = reverse_lazy('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(news, logged_in_client):
    """Для авторизованного клиента - форма комментария отображается"""
    detail_url = reverse_lazy('news:detail', args=(news.id,))
    response = logged_in_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
