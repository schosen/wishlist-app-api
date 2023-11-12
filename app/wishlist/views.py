"""
Views for the wishlist APIs
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Wishlist
from wishlist import serializers


class WishlistViewSet(viewsets.ModelViewSet):
    """View for manage wishlist APIs."""
    serializer_class = serializers.WishlistSerializer
    queryset = Wishlist.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve wishlists for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
