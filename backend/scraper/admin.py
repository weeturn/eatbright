from django.contrib import admin

from .models import Store, RawReview, Review

admin.site.register((Store, Review, RawReview))