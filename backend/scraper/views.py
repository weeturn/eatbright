from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Store, Review, RawReview
from .utils.db_operations import (  # 從 db_operations.py 導入函數
    insert_store,
    insert_reviews,
    insert_raw_review,
    read_raw_reviews_from_db,
    get_top_dishes_for_store,
    get_worst_dishes_for_store
)
from .utils.gmap_scraper import GoogleMapsScraper
from .utils.gemini_analysis import analyze_reviews_and_store_results
import json
import logging

logger = logging.getLogger(__name__)
@csrf_exempt
def scrape_and_store_reviews(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        store_name = data.get('store_name')
        google_map_url = data.get('google_map_url')

        if not store_name or not google_map_url:
            return JsonResponse({'error': 'Missing store name or URL'}, status=400)

        # 檢查 store 是否已存在
        store = Store.objects.filter(google_map_url=google_map_url).first()
        if store:
            store_id = store.id
            if Review.objects.filter(store_id=store_id).exists() and RawReview.objects.filter(store_id=store_id).exists():
                raw_reviews = RawReview.objects.filter(store_id=store_id)[:5]
                raw_reviews_data = [
                    {'text': review.text, 'relative_date': review.relative_date, 'rating': review.rating, 'user_name': review.user_name}
                    for review in raw_reviews
                ]
                top_dishes = get_top_dishes_for_store(store_id)
                worst_dishes = get_worst_dishes_for_store(store_id)

                top_dishes_data = [{'dish_name': dish['dish_name'], 'times': dish['count'], 'score': dish['average_rating']} for dish in top_dishes]
                worst_dishes_data = [{'dish_name': dish['dish_name'], 'times': dish['count'], 'score': dish['average_rating']} for dish in worst_dishes]

                return JsonResponse({
                    'raw_reviews': raw_reviews_data,
                    'top_dishes': top_dishes_data,
                    'worst_dishes': worst_dishes_data
                })

        # 如果 store 不存在，或存在但沒有相關 review/raw_review
        store_id = insert_store(store_name, google_map_url)
        with GoogleMapsScraper(debug=False) as scraper:
            scraper.sort_by(google_map_url, 1)  
            scraper.get_N_reviews(150, store_id)

        raw_reviews = RawReview.objects.filter(store_id=store_id)[:5]
        raw_reviews_data = [
            {'text': review.text, 'relative_date': review.relative_date, 'rating': review.rating, 'user_name': review.user_name}
            for review in raw_reviews
        ]

        return JsonResponse({'store_id': store_id, 'raw_reviews': raw_reviews_data})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def analyze_reviews(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        store_id = data.get('store_id')

        if not store_id:
            return JsonResponse({'error': 'Missing store ID'}, status=400)

        # Analyze reviews and store the results
        analyze_reviews_and_store_results(store_id)

        # Get top and worst dishes
        top_dishes = get_top_dishes_for_store(store_id)
        worst_dishes = get_worst_dishes_for_store(store_id)

        top_dishes_data = [{'dish_name': dish['dish_name'], 'times': dish['count'], 'score': dish['average_rating']} for dish in top_dishes]
        worst_dishes_data = [{'dish_name': dish['dish_name'], 'times': dish['count'], 'score': dish['average_rating']} for dish in worst_dishes]

        return JsonResponse({'top_dishes': top_dishes_data, 'worst_dishes': worst_dishes_data})

    return JsonResponse({'error': 'Invalid request method'}, status=405)