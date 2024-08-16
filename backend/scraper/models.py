from django.db import models
from django.utils import timezone

class Store(models.Model):
    name = models.CharField(max_length=255)
    google_map_url = models.TextField()
    def __str__(self):
        return self.name

class RawReview(models.Model):
    store = models.ForeignKey(Store, related_name='raw_reviews', on_delete=models.CASCADE)
    text = models.TextField()
    relative_date = models.CharField(max_length=50)
    retrieval_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField()
    user_name = models.CharField(max_length=255)

class Review(models.Model):
    store = models.ForeignKey(Store, related_name='reviews', on_delete=models.CASCADE)
    dish_name = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.IntegerField()
