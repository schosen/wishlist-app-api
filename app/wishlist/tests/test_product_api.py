"""
Tests for the products API.
"""

import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product, Wishlist

from wishlist.serializers import ProductSerializer


# PRODUCTS_URL = reverse('wishlist:products',  kwargs={'wishlist_id': 1})
# PRODUCT_DETAIL_URL = reverse('wishlist:product_detail',  args=(1,1))
def wishlist_product_url(wishlist_id):
    """create and return a product URL"""
    return reverse("wishlist:products", kwargs={"wishlist_id": wishlist_id})


def wishlist_product_detail_url(wishlist_id, product_id):
    """Create and return a product detail URL."""
    return reverse("wishlist:product_detail", args=[wishlist_id, product_id])


def create_user(email="user@example.com", password="testpass123"):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


def create_wishlist(user, **params):
    """Create and return a sample wishlist."""
    defaults = {
        "title": "Sample wishlist title",
        "description": "Sample description",
        "occasion_date": datetime.date(year=2020, month=1, day=1),
        "address": "123 Sample Street, Sampleland, 12QW 6ER",
    }
    defaults.update(params)

    wishlist = Wishlist.objects.create(user=user, **defaults)
    return wishlist


class PublicProductsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving products."""
        product_url = wishlist_product_url(1)
        res = self.client.get(product_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_products(self):
        """Test retrieving a list of products."""

        wishlist = create_wishlist(user=self.user)

        Product.objects.create(wishlist=wishlist, name="Pink Top", price=10.99)
        Product.objects.create(wishlist=wishlist, name="Sneakers", price=45.00)

        url = wishlist_product_url(wishlist.id)
        res = self.client.get(url)

        products = Product.objects.all().order_by("-id")
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_products_limited_to_user(self):
        """Test list of products is limited to authenticated user."""
        user2 = create_user(email="user2@example.com")
        wishlist = create_wishlist(user=user2)
        Product.objects.create(wishlist=wishlist, name="Watch", price=100.00)

        wishlist = create_wishlist(user=self.user)
        product = Product.objects.create(wishlist=wishlist, name="Jumper", price=50.00)

        url = wishlist_product_url(wishlist.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], product.name)
        self.assertEqual(res.data[0]["id"], product.id)

    def test_create_product(self):
        """Test creating a product."""
        wishlist = create_wishlist(user=self.user)

        payload = {
            "name": "Sample product",
            "price": Decimal("5.99"),
            "priority": "HIGH",
            "link": "https://youtube.com",
            "notes": "smaple notes",
        }

        url = wishlist_product_url(wishlist.id)
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.wishlist.user, self.user)

    def test_full_update(self):
        """Test full update of product."""

        wishlist = create_wishlist(user=self.user)

        product = Product.objects.create(
            wishlist=wishlist,
            name="Pink Top",
            price=10.99,
            priority="LOW",
            link="https://exmaple.com/product.pdf",
            notes="first note",
        )

        payload = {
            "name": "updated product",
            "price": Decimal("5.99"),
            "priority": "HIGH",
            "link": "https://youtube.com",
            "notes": "smaple notes",
        }

        url = wishlist_product_detail_url(wishlist.id, product.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(product, k), v)
        self.assertEqual(product.wishlist.user, self.user)

    def test_partial_update_product(self):
        """Test updating a product."""

        wishlist = create_wishlist(user=self.user)

        product = Product.objects.create(
            wishlist=wishlist,
            name="Pink Top",
            price=10.99,
            priority="LOW",
            link="https://exmaple.com/product.pdf",
            notes="first note",
        )

        payload = {"name": "Blue Top"}

        url = wishlist_product_detail_url(wishlist.id, product.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, payload["name"])

    def test_delete_product(self):
        """Test deleting an product."""

        wishlist = create_wishlist(user=self.user)

        product = Product.objects.create(
            wishlist=wishlist,
            name="Pink Top",
            price=10.99,
            priority="LOW",
            link="https://exmaple.com/product.pdf",
            notes="first note",
        )

        url = wishlist_product_detail_url(wishlist.id, product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_update_user_returns_error(self):
        """Test changing the product's user results in an error."""
        new_user = create_user(email="user2@example.com", password="test123")

        wishlist = create_wishlist(user=self.user)

        product = Product.objects.create(
            wishlist=wishlist,
            name="Pink Top",
            price=10.99,
            priority="LOW",
            link="https://exmaple.com/product.pdf",
            notes="first note",
        )

        payload = {"user": new_user.id}
        url = wishlist_product_detail_url(wishlist.id, product.id)
        self.client.patch(url, payload)

        product.refresh_from_db()
        self.assertEqual(product.wishlist.user, self.user)

    def test_delete_other_users_product_error(self):
        """Test trying to delete another users product gives error."""
        new_user = create_user(email="user2@example.com", password="test123")

        wishlist = create_wishlist(user=new_user)

        product = Product.objects.create(
            wishlist=wishlist,
            name="Pink Top",
            price=10.99,
            priority="LOW",
            link="https://exmaple.com/product.pdf",
            notes="first note",
        )

        url = wishlist_product_detail_url(wishlist.id, product.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(id=product.id).exists())

    def test_create_other_users_product_error(self):
        """Test trying to create another users product gives error."""
        new_user = create_user(email="user2@example.com", password="test123")

        wishlist = create_wishlist(user=new_user)

        url = wishlist_product_url(wishlist.id)

        payload = {
            "name": "Sample product",
            "price": Decimal("5.99"),
            "priority": "HIGH",
            "link": "https://youtube.com",
            "notes": "smaple notes",
        }

        res = self.client.post(url, payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Product.objects.filter(name=payload["name"]).exists())

    def test_list_other_users_product_error(self):
        """Test trying to list another users product gives error."""
        new_user = create_user(email="user2@example.com", password="test123")

        wishlist = create_wishlist(user=new_user)

        product = Product.objects.create(
            wishlist=wishlist,
            name="Pink Top",
            price=10.99,
            priority="LOW",
            link="https://exmaple.com/product.pdf",
            notes="first note",
        )

        url = wishlist_product_detail_url(wishlist.id, product.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_partial_update_other_users_product_error(self):
        """Test trying to partial update another users product gives error."""
        new_user = create_user(email="user2@example.com", password="test123")

        wishlist = create_wishlist(user=new_user)

        product = Product.objects.create(
            wishlist=wishlist,
            name="Pink Top",
            price=10.99,
            priority="LOW",
            link="https://exmaple.com/product.pdf",
            notes="first note",
        )

        url = wishlist_product_detail_url(wishlist.id, product.id)

        payload = {"products": {"name": "New Product Name"}}

        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(
            Product.objects.filter(name=payload["products"]["name"]).exists()
        )
