"""
Views for the wishlist APIs
"""

# from drf_spectacular.utils import (
#     extend_schema_view,
#     extend_schema,
#     OpenApiParameter,
#     OpenApiTypes,
# )
from rest_framework import (
    viewsets,
    # mixins
)
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.generics import get_object_or_404

# from rest_framework.views import APIView
# from drf_spectacular.types import OpenApiTypes


from core.models import Wishlist, Product
from wishlist import serializers


# @extend_schema_view(
#     list=extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 'products',
#                 OpenApiTypes.STR,
#                 description='Comma separated list of product IDs to filter',
#             ),
#         ]
#     )
# )


class UserOwnsWishlist(BasePermission):

    def has_permission(self, request, view):
        wishlist_id = view.kwargs.get("wishlist_id")
        if wishlist_id is None:
            return False

        get_object_or_404(
            Wishlist,
            id=wishlist_id,
            user_id=request.user.id,
        )
        return True


class WishlistViewSet(viewsets.ModelViewSet):
    """View for manage wishlist APIs."""

    serializer_class = serializers.WishlistDetailSerializer
    queryset = Wishlist.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve wishlists for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return serializers.WishlistSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new wishlist."""
        serializer.save(user=self.request.user)


# class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """Manage products in the database."""

#     serializer_class = serializers.ProductSerializer(many=True)
#     queryset = Product.objects.all()
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         """Filter queryset to authenticated user."""
#         return self.queryset.filter(user=self.request.user).order_by('-id')


class ProductViewSet(generics.ListCreateAPIView):
    """Manage products in the database."""

    serializer_class = serializers.ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, UserOwnsWishlist]
    lookup_url_kwarg = "product_id"

    def get_queryset(self):
        """Filter queryset to specific wishlist key user."""
        if self.kwargs.get("wishlist_id"):
            return self.queryset.filter(
                wishlist_id=self.kwargs.get("wishlist_id")
            ).order_by("-id")
        # should return an error?
        return self.queryset.all()

    def perform_create(self, serializer):
        serializer.save(wishlist_id=self.kwargs.get("wishlist_id"))


class ProductDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
    """Manage products detail in the database."""

    serializer_class = serializers.ProductSerializer
    queryset = Product.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, UserOwnsWishlist]

    def get_object(self):
        if self.kwargs.get("wishlist_id"):
            return get_object_or_404(
                self.get_queryset(),
                wishlist_id=self.kwargs.get("wishlist_id"),
                id=self.kwargs.get("product_id"),
            )
        return get_object_or_404(self.get_queryset(),
                                 id=self.kwargs.get("product_id"))
