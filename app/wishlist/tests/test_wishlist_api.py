"""
Tests for recipe APIs.
"""
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Wishlist

from wishlist.serializers import WishlistSerializer


WISHLIST_URL = reverse('wishlist:wishlist-list')


def create_wishlist(user, **params):
    """Create and return a sample wishlist."""
    defaults = {
        'title': 'Sample wishlist title',
        'description': 'Sample description',
        'occasion_date': datetime.date(year=2020, month=1, day=1),
        'address': '123 Sample Street, Sampleland, 12QW 6ER'
    }
    defaults.update(params)

    wishlist = Wishlist.objects.create(user=user, **defaults)
    return wishlist


class PublicWishlistAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(WISHLIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWishlistApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_wishlist(self):
        """Test retrieving a list of wishlist."""
        create_wishlist(user=self.user)
        create_wishlist(user=self.user)

        res = self.client.get(WISHLIST_URL)

        wishlist = Wishlist.objects.all().order_by('-id')
        serializer = WishlistSerializer(wishlist, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_wishlist_list_limited_to_user(self):
        """Test list of wishlist is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_wishlist(user=other_user)
        create_wishlist(user=self.user)

        res = self.client.get(WISHLIST_URL)

        wishlist = Wishlist.objects.filter(user=self.user)
        serializer = WishlistSerializer(wishlist, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

# "TO-DO: CREATE API FOR USER TO DELETE ALL WISHLISTS"