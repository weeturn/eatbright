from ..models import Store, Review, RawReview
from django.db import transaction
from django.db.models import Count, Avg

def insert_store(name, google_map_url):
    try:
        store = Store.objects.create(name=name, google_map_url=google_map_url)
        return store.id
    except Exception as e:
        print(f"Error: {e}")
        return None

def insert_reviews(store_id, reviews):
    try:
        with transaction.atomic():
            for review in reviews:
                Review.objects.create(
                    store_id=store_id,
                    dish_name=review[0],
                    description=review[1],
                    rating=int(review[2])
                )
        print('Insert reviews done !!')
    except Exception as e:
        print(f"Error: {e}")

def insert_raw_review(store_id, text, relative_date, rating, user_name):
    try:
        raw_review = RawReview.objects.create(
            store_id=store_id,
            text=text,
            relative_date=relative_date,
            rating=rating,
            user_name=user_name
        )
        return raw_review.id
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_raw_reviews_from_db(store_id):
    try:
        raw_reviews = RawReview.objects.filter(store_id=store_id)
        reviews = [review.text for review in raw_reviews]
        return reviews
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_top_dishes_for_store(store_id):
    try:
        result = (
            Review.objects.filter(store_id=store_id)
            .values('dish_name')
            .annotate(count=Count('id'), average_rating=Avg('rating'))
            .filter(count__gt=2)
            .order_by('-average_rating', '-count')[:7]
        )
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_worst_dishes_for_store(store_id):
    try:
        result = (
            Review.objects.filter(store_id=store_id)
            .values('dish_name')
            .annotate(count=Count('id'), average_rating=Avg('rating'))
            .filter(count__gt=2)
            .order_by('average_rating', '-count')[:5]
        )
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []
