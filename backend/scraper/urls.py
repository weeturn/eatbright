# from django.urls import path

# from . import views

# urlpatterns = [
#     path("", views.scrape_and_store_reviews, name="scrape_and_store_reviews"),
#     path("", views.read_raw_reviews_from_db, name="read_raw_reviews_from_db"),
# ]

from django.urls import path
from .views import scrape_and_store_reviews, analyze_reviews

urlpatterns = [
    path('scraper/', scrape_and_store_reviews, name='scrape_and_store_reviews'),
    path('gemini/', analyze_reviews, name='analyze_reviews'),
]