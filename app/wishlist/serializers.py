"""
Serializers for wishlist APIs
"""

from rest_framework import serializers

from core.models import Wishlist, Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""

    class Meta:
        model = Product
        fields = ["id", "name", "link", "priority", "price", "notes"]
        read_only_fields = ["id"]


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlists."""

    products = ProductSerializer(many=True, required=False)

    class Meta:
        model = Wishlist
        fields = ["id", "title", "occasion_date", "products"]
        read_only_fields = ["id"]

    # customize method so that we can override the
    # frameworks create/write method to create products via wishlist
    # rather than just read
    def create(self, validated_data):
        """Create a wishlist and its products."""
        products = validated_data.pop("products", [])
        wishlist = Wishlist.objects.create(**validated_data)
        # request authenticated user data
        # auth_user = self.context['request'].user
        for product in products:

            product_obj, created = Product.objects.get_or_create(
                wishlist=wishlist,
                # user=auth_user,
                **product,
            )
            wishlist.products.add(product_obj)

        return wishlist

    def update(self, instance, validated_data):
        """Update a wishlist and its products"""

        # Update or create nested Product objects
        product_data = validated_data.pop("products", None)

        if product_data is not None:

            # this detaches the relationship between product
            # and wishlist (set id to null)
            # instance.products.clear()
            for product_item in product_data:
                product_instance, created = Product.objects.get_or_create(
                    **product_item, wishlist=instance
                )

                # below commented out works the same as instance.products.add
                # (product_instance) need to understand the difference
                # ProductSerializer().update(product_instance, product_item)

                instance.products.add(product_instance)
            if len(product_data) == 0:
                instance.products.all().delete()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class WishlistDetailSerializer(WishlistSerializer):
    """Serializer for wishlist detail view."""

    class Meta(WishlistSerializer.Meta):
        # TO-DO: this should have a list of wishlist items
        fields = WishlistSerializer.Meta.fields + ["description", "address"]
