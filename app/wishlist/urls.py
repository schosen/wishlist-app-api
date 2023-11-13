"""
URL mappings for the wishlist app.
"""
from django.urls import (
    path,
    include,
)

# default router provided by api rest framework, auto creates routes for all options (put, post, get etc)
from rest_framework.routers import DefaultRouter

from wishlist import views


router = DefaultRouter()
router.register('wishlists', views.WishlistViewSet)

app_name = 'wishlist'

urlpatterns = [
    path('', include(router.urls)),
]
