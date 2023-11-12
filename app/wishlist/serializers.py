"""
Serializers for wishlist APIs
"""
from rest_framework import serializers

from core.models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlists."""

    class Meta:
        model = Wishlist
        fields = ['id', 'title', 'occasion_date', 'address']
        read_only_fields = ['id']
